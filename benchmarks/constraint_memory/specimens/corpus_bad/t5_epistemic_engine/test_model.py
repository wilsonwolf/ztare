import math
import random
import collections
import inspect
import numpy as np # For matrix operations

# --- LOAD-BEARING VARIABLES (System Parameters & Simulated Real-World Values) ---
epsilon = 0.001 # Initial perturbation magnitude for numerical derivative calculation
adam_beta1 = 0.9 # Adam optimizer parameter: decay rate for first moment estimates (m)
adam_beta2 = 0.999 # Adam optimizer parameter: decay rate for second moment estimates (v)
adam_epsilon_stabilizer = 1e-8 # Adam optimizer parameter: small constant to prevent division by zero
learning_rate_model_params = 0.001 # Global learning rate scale for all model parameters (weights/biases)
learning_rate_axiom_coeffs = 0.01 # NEW: Learning rate scale specifically for axiom coefficients
min_observations_for_calibration = 200 # Minimum Z_actual observations before BSS can be robustly calculated
target_brier_skill_score = 0.20 # Minimum acceptable Brier Skill Score after calibration
rolling_window_size = 50 # Number of observations for rolling average Brier Skill Score calculation
hidden_layer_size = 4 # Number of neurons in the ThesisPredictor's hidden layer

initial_axiom_coefficient_value = 0.5 # NEW: Initial value for axiom coefficients within ThesisPredictor
axiom_sync_frequency = 1 # NEW: Frequency for Meta-Judge to sync learned axiom coefficients

hypothetical_economy_growth_rate_q1_2025_base = 0.02 # Baseline for simulated economy growth rate
hypothetical_inflation_rate_q1_2025_base = 0.03 # Baseline for simulated inflation rate

true_bias_nl = -0.5 # Intercept term for the *simulated non-linear* Z_actual function
true_growth_freq_nl = 50 # Frequency parameter for sine component of *simulated non-linear* growth effect
true_growth_coeff_nl = 10 # Coefficient for sine component of *simulated non-linear* growth effect
true_inflation_freq_nl = 30 # Frequency parameter for cosine component of *simulated non-linear* inflation effect
true_inflation_coeff_nl = -15 # Coefficient for cosine component of *simulated non-linear* inflation effect
true_interaction_coeff_nl = 500 # Coefficient for interaction term (growth_rate * inflation_rate)
true_axiom_relevance = 0.8 # Relevance of AXIOM_RECESSION_AVOIDANCE in the *simulated non-linear* Z_actual

differentiability_tolerance = 0.05 # NEW: Max allowed absolute difference between perturbation gradients for DifferentiabilityRobustnessCheck
robustness_perturbation_epsilon_scales = [0.00001, 0.0001, 0.001] # NEW: Array of epsilon scales for robustness check


class ThesisPredictor:
    """
    Simulates the Mutator's output: a thesis's prediction model.
    Axioms are treated as learnable parameters within the MLP.
    """
    def __init__(self, external_input_size: int, hidden_size: int, output_size: int = 1,
                 axiom_initial_weights: dict = None):
        
        self.external_input_size = external_input_size 
        
        self.learned_axiom_coeffs = {}
        if axiom_initial_weights:
            for axiom_name, initial_value in axiom_initial_weights.items():
                self.learned_axiom_coeffs[axiom_name] = np.array([initial_value], dtype=np.float64) # Make it a numpy array for consistent gradient calculation
        else:
            raise ValueError("ThesisPredictor must be initialized with axiom_initial_weights for its learnable coefficients.")

        self.axiom_names = sorted(list(self.learned_axiom_coeffs.keys()))
        self.num_axioms = len(self.axiom_names)
        
        # Total input features for the first layer (external inputs + axiom coefficients)
        total_input_features_to_mlp = self.external_input_size + self.num_axioms

        # Initialize MLP weights and biases with the *correct* total input dimension
        self.weights_ih = np.random.randn(total_input_features_to_mlp, hidden_size).astype(np.float64) * 0.1 
        self.bias_h = np.zeros((1, hidden_size), dtype=np.float64) 
        self.weights_ho = np.random.randn(hidden_size, output_size).astype(np.float64) * 0.1 
        self.bias_o = np.zeros((1, output_size), dtype=np.float64) 

    def _relu(self, x):
        return np.maximum(0, x)

    def _sigmoid(self, x):
        return 1 / (1 + np.exp(-np.clip(x, -500, 500))) 

    def calculate_p_predicted(self, load_bearing_variables: dict) -> float:
        """
        Calculates the predicted probability of an event (Z_actual=1) using an MLP.
        This function now explicitly uses load-bearing variables and *internal* learnable axiom coefficients.
        """
        # Prepare input vector (external load-bearing variables + internal axiom coefficients)
        growth_rate = load_bearing_variables.get('hypothetical_economy_growth_rate_q1_2025', 0.0)
        inflation_rate = load_bearing_variables.get('hypothetical_inflation_rate_q1_2025', 0.0)
        
        external_inputs = np.array([growth_rate, inflation_rate], dtype=np.float64)
        
        axiom_inputs = np.array([self.learned_axiom_coeffs[name].item() for name in self.axiom_names], dtype=np.float64)
        
        input_vector_to_mlp = np.concatenate((external_inputs, axiom_inputs)).reshape(1, -1)

        if input_vector_to_mlp.shape[1] != self.weights_ih.shape[0]:
            raise ValueError(f"Input vector dimension mismatch: {input_vector_to_mlp.shape[1]} vs {self.weights_ih.shape[0]}. "
                             "This indicates an architectural inconsistency in how inputs are constructed vs weights initialized.")

        hidden_layer_input = np.dot(input_vector_to_mlp, self.weights_ih) + self.bias_h
        hidden_layer_output = self._relu(hidden_layer_input)

        output_layer_input = np.dot(hidden_layer_output, self.weights_ho) + self.bias_o
        p_predicted = self._sigmoid(output_layer_input).flatten()[0]

        return p_predicted

    def get_all_params(self):
        """Returns a dictionary of all optimizable parameters (MLP weights/biases + axiom coefficients)."""
        params = {
            'weights_ih': self.weights_ih,
            'bias_h': self.bias_h,
            'weights_ho': self.weights_ho,
            'bias_o': self.bias_o,
        }
        params.update(self.learned_axiom_coeffs) 
        return params

    def set_all_params(self, params_dict):
        """Sets all optimizable parameters from a dictionary."""
        self.weights_ih = params_dict['weights_ih']
        self.bias_h = params_dict['bias_h']
        self.weights_ho = params_dict['weights_ho']
        self.bias_o = params_dict['bias_o']
        for axiom_name in self.learned_axiom_coeffs: 
            self.learned_axiom_coeffs[axiom_name] = params_dict[axiom_name]


class FiringSquad:
    """
    Executes the ThesisPredictor, implements Robust Sensitivity Attributor (RSA),
    and now includes DifferentiabilityRobustnessCheck.
    """
    def calculate_sensitivity_report(self, thesis_predictor: ThesisPredictor,
                                     load_bearing_variables: dict,
                                     current_epsilon: float) -> dict:
        """
        Computes dP/d(param) for all parameters (weights/biases + axiom coefficients) of the ThesisPredictor
        using central difference.
        """
        sensitivity_vector = {}
        original_params = {k: v.copy() for k, v in thesis_predictor.get_all_params().items()}

        P_predicted_baseline = thesis_predictor.calculate_p_predicted(load_bearing_variables)

        for param_name, param_array in original_params.items():
            flat_param = param_array.flatten()
            dP_d_param_flat = np.zeros_like(flat_param, dtype=np.float64)

            # Only calculate derivatives for single-element axiom coefficients or MLP parameters
            if param_name in thesis_predictor.learned_axiom_coeffs or param_name in ['weights_ih', 'bias_h', 'weights_ho', 'bias_o']:
                for i in range(len(flat_param)):
                    # Perturb +epsilon
                    perturbed_params_plus = {k: v.copy() for k, v in original_params.items()}
                    temp_flat_plus = perturbed_params_plus[param_name].flatten()
                    temp_flat_plus[i] += current_epsilon
                    perturbed_params_plus[param_name] = temp_flat_plus.reshape(param_array.shape)
                    thesis_predictor.set_all_params(perturbed_params_plus)
                    P_plus = thesis_predictor.calculate_p_predicted(load_bearing_variables)

                    # Perturb -epsilon
                    perturbed_params_minus = {k: v.copy() for k, v in original_params.items()}
                    temp_flat_minus = perturbed_params_minus[param_name].flatten()
                    temp_flat_minus[i] -= current_epsilon
                    perturbed_params_minus[param_name] = temp_flat_minus.reshape(param_array.shape)
                    thesis_predictor.set_all_params(perturbed_params_minus)
                    P_minus = thesis_predictor.calculate_p_predicted(load_bearing_variables)

                    dP_d_param_flat[i] = (P_plus - P_minus) / (2 * current_epsilon)
                
                sensitivity_vector[param_name] = dP_d_param_flat.reshape(param_array.shape)
        
        thesis_predictor.set_all_params(original_params) # Restore original parameters

        return {
            "P_predicted_baseline": P_predicted_baseline,
            "sensitivity_vector": sensitivity_vector
        }

    def differentiability_robustness_check(self, thesis_predictor: ThesisPredictor,
                                           load_bearing_variables: dict,
                                           epsilon_scales: list,
                                           tolerance: float) -> dict:
        """
        NEW: Computes numerical gradients for each axiom coefficient using multiple epsilon scales
        and checks for consistency, detecting non-differentiable exploits.
        Returns a dictionary with 'pass' status and 'gradient_consistency_scores' for each axiom.
        """
        check_results = {"pass": True, "gradient_consistency_scores": {}}
        original_params = {k: v.copy() for k, v in thesis_predictor.get_all_params().items()}

        for axiom_name in thesis_predictor.learned_axiom_coeffs.keys():
            gradients_at_scales = []
            
            for eps in epsilon_scales:
                param_array = original_params[axiom_name]
                if param_array.shape != (1,): # Only check scalar axiom coeffs
                    continue # Skip if not a scalar axiom coefficient
                
                # Perturb +eps
                perturbed_params_plus = {k: v.copy() for k, v in original_params.items()}
                perturbed_params_plus[axiom_name][0] += eps
                thesis_predictor.set_all_params(perturbed_params_plus)
                P_plus = thesis_predictor.calculate_p_predicted(load_bearing_variables)

                # Perturb -eps
                perturbed_params_minus = {k: v.copy() for k, v in original_params.items()}
                perturbed_params_minus[axiom_name][0] -= eps
                thesis_predictor.set_all_params(perturbed_params_minus)
                P_minus = thesis_predictor.calculate_p_predicted(load_bearing_variables)

                gradient = (P_plus - P_minus) / (2 * eps)
                gradients_at_scales.append(gradient)
            
            thesis_predictor.set_all_params(original_params) # Restore original params after each axiom check

            if len(gradients_at_scales) > 1:
                # Calculate the maximum absolute difference between any two gradients to assess consistency
                max_diff = 0.0
                for i in range(len(gradients_at_scales)):
                    for j in range(i + 1, len(gradients_at_scales)):
                        max_diff = max(max_diff, abs(gradients_at_scales[i] - gradients_at_scales[j]))
                
                check_results["gradient_consistency_scores"][axiom_name] = max_diff
                if max_diff > tolerance:
                    check_results["pass"] = False
            elif len(gradients_at_scales) == 1:
                 # If only one scale, it's vacuously consistent, assign 0 score
                 check_results["gradient_consistency_scores"][axiom_name] = 0.0
            else: # No scales provided
                 check_results["gradient_consistency_scores"][axiom_name] = np.inf # Indicate failure to check
                 check_results["pass"] = False

        return check_results


class EpistemicGradientUpdater:
    """
    Upgrades to use Adam optimizer for robust updates of all ThesisPredictor parameters,
    including new axiom coefficients.
    """
    def __init__(self, learning_rate_model_params, learning_rate_axiom_coeffs, beta1, beta2, epsilon_stabilizer):
        self.learning_rate_model_params = learning_rate_model_params
        self.learning_rate_axiom_coeffs = learning_rate_axiom_coeffs
        self.beta1 = beta1
        self.beta2 = beta2
        self.epsilon_stabilizer = epsilon_stabilizer
        self.m = {} 
        self.v = {} 
        self.t = 0 

    def update(self, thesis_predictor: ThesisPredictor, sensitivity_report: dict, Z_actual: float):
        self.t += 1
        P_predicted = sensitivity_report["P_predicted_baseline"]
        sensitivity_vector = sensitivity_report["sensitivity_vector"]

        dBS_dP = 2 * (P_predicted - Z_actual) # Derivative of Brier Score w.r.t P_predicted

        current_params = thesis_predictor.get_all_params()
        new_params = {k: v.copy() for k, v in current_params.items()}

        for param_name, param_array in current_params.items():
            dP_d_param = sensitivity_vector.get(param_name, np.zeros_like(param_array, dtype=np.float64))
            gradient = dBS_dP * dP_d_param

            if param_name not in self.m:
                self.m[param_name] = np.zeros_like(param_array, dtype=np.float64)
                self.v[param_name] = np.zeros_like(param_array, dtype=np.float64)

            self.m[param_name] = self.beta1 * self.m[param_name] + (1 - self.beta1) * gradient
            self.v[param_name] = self.beta2 * self.v[param_name] + (1 - self.beta2) * (gradient ** 2)

            m_hat = self.m[param_name] / (1 - self.beta1 ** self.t)
            v_hat = self.v[param_name] / (1 - self.beta2 ** self.t)

            current_lr = self.learning_rate_axiom_coeffs if param_name in thesis_predictor.learned_axiom_coeffs else self.learning_rate_model_params

            new_params[param_name] -= current_lr * m_hat / (np.sqrt(v_hat) + self.epsilon_stabilizer)
        
        thesis_predictor.set_all_params(new_params)


class MetaJudge:
    """
    Scores thesis, manages ThesisPredictor parameters (via updater), enforces architectural validation,
    syncs learned axiom coefficients, and now enforces AxiomDifferentiabilityVeto.
    """
    def __init__(self, external_input_size, hidden_size, output_size):
        self.axiom_weights = {'AXIOM_RECESSION_AVOIDANCE': initial_axiom_coefficient_value} 
        
        self.thesis_predictor = ThesisPredictor(
            external_input_size=external_input_size, 
            hidden_size=hidden_size,
            output_size=output_size,
            axiom_initial_weights=self.axiom_weights
        )
        
        self.epistemic_updater = EpistemicGradientUpdater(
            learning_rate_model_params, learning_rate_axiom_coeffs, adam_beta1, adam_beta2, adam_epsilon_stabilizer
        )
        self.firing_squad = FiringSquad()
        self.current_epsilon = epsilon 

    def validate_thesis_predictor_architecture(self, predictor: ThesisPredictor):
        """
        Gatekeeper Reality: Validates ThesisPredictor signature, output range, MLP structure,
        and crucially, its implementation of learnable axiom coefficients.
        """
        if not hasattr(predictor, 'calculate_p_predicted'):
            raise ValueError("Meta-Judge VETO: ThesisPredictor must have 'calculate_p_predicted' method.")
        sig = inspect.signature(predictor.calculate_p_predicted)
        params = list(sig.parameters.keys())
        required_params = ['load_bearing_variables'] 
        if not all(p in params for p in required_params):
            raise ValueError(
                f"Meta-Judge VETO: ThesisPredictor.calculate_p_predicted must accept {required_params} as arguments. Found {params}."
            )

        required_attributes = ['weights_ih', 'bias_h', 'weights_ho', 'bias_o', '_relu', '_sigmoid', 'learned_axiom_coeffs']
        for attr in required_attributes:
            if not hasattr(predictor, attr):
                raise ValueError(f"Meta-Judge VETO: ThesisPredictor must implement MLP structure (missing '{attr}' attribute).")
        
        # AxiomCoeffValidation: Verify learnable axiom coefficients
        if not isinstance(predictor.learned_axiom_coeffs, dict) or not predictor.learned_axiom_coeffs:
            raise ValueError("Meta-Judge VETO: ThesisPredictor must have a 'learned_axiom_coeffs' dictionary for axiom parameters.")
        for axiom_name in self.axiom_weights.keys():
            if axiom_name not in predictor.learned_axiom_coeffs or not isinstance(predictor.learned_axiom_coeffs[axiom_name], np.ndarray):
                raise ValueError(f"Meta-Judge VETO: ThesisPredictor missing learnable coefficient for axiom '{axiom_name}' or it's not a numpy array.")
            if predictor.learned_axiom_coeffs[axiom_name].shape != (1,):
                raise ValueError(f"Meta-Judge VETO: Axiom coefficient for '{axiom_name}' must be a scalar numpy array (shape (1,)).")

        # Input dimension consistency check for weights_ih
        expected_input_features = predictor.external_input_size + predictor.num_axioms
        if predictor.weights_ih.shape[0] != expected_input_features:
             raise ValueError(f"Meta-Judge VETO: ThesisPredictor's weights_ih input dimension ({predictor.weights_ih.shape[0]}) "
                              f"does not match expected total input features ({expected_input_features}). "
                              "Ensure external_input_size + num_axioms == weights_ih.shape[0]")

        dummy_load_bearing_variables = {
            'hypothetical_economy_growth_rate_q1_2025': hypothetical_economy_growth_rate_q1_2025_base,
            'hypothetical_inflation_rate_q1_2025': hypothetical_inflation_rate_q1_2025_base
        }
        test_p = predictor.calculate_p_predicted(dummy_load_bearing_variables)
        if not (0.0 <= test_p <= 1.0):
            raise ValueError(f"Meta-Judge VETO: ThesisPredictor.calculate_p_predicted output ({test_p}) must be within [0, 1].")

    def sync_axiom_weights_from_predictor(self):
        """
        AxiomWeightSynchronization Protocol: Updates the Meta-Judge's global axiom_weights
        store with the empirically learned coefficients from the ThesisPredictor.
        """
        for axiom_name, learned_coeff_array in self.thesis_predictor.learned_axiom_coeffs.items():
            self.axiom_weights[axiom_name] = learned_coeff_array.item()

    def evaluate_and_update(self, load_bearing_variables: dict, Z_actual: float, iteration: int, current_epsilon: float):
        """
        Orchestrates evaluation, sensitivity calculation, and parameter updates.
        Includes DifferentiabilityRobustnessCheck and veto.
        """
        self.validate_thesis_predictor_architecture(self.thesis_predictor)

        # AxiomDifferentiabilityVeto: Perform robustness check
        differentiability_check_results = self.firing_squad.differentiability_robustness_check(
            self.thesis_predictor, load_bearing_variables, robustness_perturbation_epsilon_scales, differentiability_tolerance
        )

        if not differentiability_check_results["pass"]:
            # If any axiom is non-differentiable or gamed, veto the entire thesis
            inconsistent_axioms = [
                ax for ax, score in differentiability_check_results["gradient_consistency_scores"].items()
                if score > differentiability_tolerance
            ]
            raise ValueError(
                f"Meta-Judge VETO (AxiomDifferentiabilityVeto): Thesis contains non-differentiable or gamed axiom(s): {inconsistent_axioms}. "
                "Gradient consistency scores: " + str({ax: f"{score:.6f}" for ax, score in differentiability_check_results["gradient_consistency_scores"].items()})
            )

        sensitivity_report = self.firing_squad.calculate_sensitivity_report(
            self.thesis_predictor, load_bearing_variables, current_epsilon
        )

        self.epistemic_updater.update(
            self.thesis_predictor, sensitivity_report, Z_actual
        )
        
        if iteration % axiom_sync_frequency == 0:
            self.sync_axiom_weights_from_predictor()
        
        return sensitivity_report["P_predicted_baseline"], differentiability_check_results["gradient_consistency_scores"]

# --- Simulation and Falsification Test ---
def test_model():
    print("Running Falsification Test for V3 Architecture (Axiom Credit Assignment & LLM Bridge) with Differentiability Robustness...")

    external_input_features = 2 
    meta_judge = MetaJudge(external_input_features, hidden_layer_size, output_size=1)

    brier_scores = collections.deque(maxlen=rolling_window_size)
    actual_events_history = [] 
    differentiability_scores_history = collections.defaultdict(list)

    for i in range(min_observations_for_calibration):
        current_epsilon_for_sensitivity = epsilon * (1 - i / min_observations_for_calibration) + 1e-6 

        current_load_bearing_variables = {
            'hypothetical_economy_growth_rate_q1_2025': random.uniform(
                hypothetical_economy_growth_rate_q1_2025_base * 0.8,
                hypothetical_economy_growth_rate_q1_2025_base * 1.2
            ),
            'hypothetical_inflation_rate_q1_2025': random.uniform(
                hypothetical_inflation_rate_q1_2025_base * 0.8,
                hypothetical_inflation_rate_q1_2025_base * 1.2
            )
        }
        
        growth_rate_val = current_load_bearing_variables['hypothetical_economy_growth_rate_q1_2025']
        inflation_rate_val = current_load_bearing_variables['hypothetical_inflation_rate_q1_2025']

        # True underlying process (smoothly non-linear and differentiable)
        true_linear_combination_nl = (
            true_bias_nl
            + true_growth_coeff_nl * math.sin(growth_rate_val * true_growth_freq_nl)
            + true_inflation_coeff_nl * math.cos(inflation_rate_val * true_inflation_freq_nl)
            + true_interaction_coeff_nl * growth_rate_val * inflation_rate_val
            + true_axiom_relevance * 1.0 # The axiom's true impact is hardcoded here (as if axiom is fully 'true')
        )
        true_prob_avoid_recession = 1 / (1 + math.exp(-true_linear_combination_nl))
        
        Z_actual = 1 if random.random() < true_prob_avoid_recession else 0
        actual_events_history.append(Z_actual)

        P_predicted, grad_consistency_scores = meta_judge.evaluate_and_update(
            current_load_bearing_variables, Z_actual, i+1, current_epsilon_for_sensitivity
        )

        for axiom_name, score in grad_consistency_scores.items():
            differentiability_scores_history[axiom_name].append(score)

        current_brier_score = (P_predicted - Z_actual)**2
        brier_scores.append(current_brier_score)

        if i >= rolling_window_size - 1:
            BS_model = sum(brier_scores) / len(brier_scores)
            rolling_historical_freq = sum(actual_events_history[-rolling_window_size:]) / rolling_window_size
            BS_reference = rolling_historical_freq * (1 - rolling_historical_freq)
            
            if BS_reference < 1e-9: 
                BS_reference = 1e-9 

            BSS = 1 - (BS_model / BS_reference)
            
            tracked_weight_ih_0_0 = meta_judge.thesis_predictor.weights_ih[0, 0] # Growth_rate to hidden[0]
            tracked_axiom_coeff = meta_judge.thesis_predictor.learned_axiom_coeffs['AXIOM_RECESSION_AVOIDANCE'].item()
            global_axiom_weight_synced = meta_judge.axiom_weights['AXIOM_RECESSION_AVOIDANCE']
            current_grad_consistency_score = grad_consistency_scores.get('AXIOM_RECESSION_AVOIDANCE', np.nan)


            print(f"Obs {i+1:3d}: P_pred={P_predicted:.3f}, Z_actual={Z_actual}, BS_model={BS_model:.4f}, BSS={BSS:.3f}, W_ih[0,0]={tracked_weight_ih_0_0:.3f}, LearnedAxiomCoeff={tracked_axiom_coeff:.3f}, SyncedAxiomWeight={global_axiom_weight_synced:.3f}, GradConsistency={current_grad_consistency_score:.5f}, Epsilon_sens={current_epsilon_for_sensitivity:.5f}")

            if i == min_observations_for_calibration - 1:
                print(f"\n--- Falsification Test Results after {min_observations_for_calibration} observations ---")
                
                final_bss = BSS
                print(f"Final Rolling Brier Skill Score over last {rolling_window_size} observations: {final_bss:.3f}")
                assert final_bss >= target_brier_skill_score, \
                    f"FALSIFICATION FAILED: Rolling Brier Skill Score ({final_bss:.3f}) did not meet target ({target_brier_skill_score})."

                final_learned_axiom_coeff = meta_judge.thesis_predictor.learned_axiom_coeffs['AXIOM_RECESSION_AVOIDANCE'].item()
                print(f"Final Learned AXIOM_RECESSION_AVOIDANCE coefficient: {final_learned_axiom_coeff:.3f}")
                assert final_learned_axiom_coeff > 0.65, \
                    f"FALSIFICATION FAILED: Learned AXIOM_RECESSION_AVOIDANCE coefficient ({final_learned_axiom_coeff:.3f}) " \
                    f"did not converge to a value indicative of its high true relevance (target > 0.65)."
                assert abs(final_learned_axiom_coeff - true_axiom_relevance) < 0.25, \
                    f"FALSIFICATION FAILED: Learned AXIOM_RECESSION_AVOIDANCE coefficient ({final_learned_axiom_coeff:.3f}) " \
                    f"is not sufficiently close to true relevance ({true_axiom_relevance:.3f}) within tolerance (0.25)."

                final_synced_axiom_weight = meta_judge.axiom_weights['AXIOM_RECESSION_AVOIDANCE']
                print(f"Final Synced Global AXIOM_RECESSION_AVOIDANCE weight: {final_synced_axiom_weight:.3f}")
                assert abs(final_synced_axiom_weight - final_learned_axiom_coeff) < 1e-6, \
                    f"FALSIFICATION FAILED: Global axiom weight ({final_synced_axiom_weight:.3f}) " \
                    f"did not accurately reflect learned coefficient ({final_learned_axiom_coeff:.3f}) after sync."
                
                # Assert for Differentiability Check:
                # Check if all historical differentiability scores for the axiom consistently passed
                all_differentiability_scores = differentiability_scores_history['AXIOM_RECESSION_AVOIDANCE']
                if not all_differentiability_scores: # Defensive check if axiom was never processed for some reason
                    raise AssertionError("FALSIFICATION FAILED: No differentiability scores recorded for AXIOM_RECESSION_AVOIDANCE.")

                avg_differentiability_score = np.mean(all_differentiability_scores)
                max_differentiability_score = np.max(all_differentiability_scores)

                print(f"Average Differentiability Consistency Score for AXIOM_RECESSION_AVOIDANCE: {avg_differentiability_score:.6f}")
                print(f"Max Differentiability Consistency Score for AXIOM_RECESSION_AVOIDANCE: {max_differentiability_score:.6f}")
                assert max_differentiability_score <= differentiability_tolerance, \
                    f"FALSIFICATION FAILED: Axiom's differentiability consistency check failed. Max score ({max_differentiability_score:.6f}) " \
                    f"exceeded tolerance ({differentiability_tolerance:.6f}), indicating potential non-differentiable exploit."

    print("\nFalsification Test PASSED: All conditions met, demonstrating robust axiom credit assignment, empirical calibration, a functional bridge to the global axiom store, AND confirmed differentiability robustness.")

if __name__ == "__main__":
    test_model()
