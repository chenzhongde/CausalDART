

class Sigma:
    """
    A representation of the sigma term in the model.
    Specifically, this is the sigma of y itself, i.e. the sigma in
        y ~ Normal(sum_of_trees, sigma)

    The default prior is an inverse gamma distribution on the variance
    The parametrization is slightly different to the numpy gamma version, with the scale parameter inverted

    Parameters
    ----------
    alpha - the shape of the prior
    beta - the scale of the prior
    scaling_factor - the range of the original distribution
                     needed to rescale the variance into the original scale rather than on (-0.5, 0.5)

    """

    def __init__(self, alpha: float, beta: float, scaling_factor: float):
        #print("enter bartpy/bartpy/sigma.py Sigma __init__")        
        self.alpha = alpha
        self.beta = beta
        self._current_value = 1.0
        self.scaling_factor = scaling_factor
        #print("-exit bartpy/bartpy/sigma.py Sigma __init__")

    def set_value(self, value: float) -> None:
        #print("enter bartpy/bartpy/sigma.py Sigma set_value")
        #print("-exit bartpy/bartpy/sigma.py Sigma set_value")
        self._current_value = value

    def current_value(self) -> float:
        #print("enter bartpy/bartpy/sigma.py Sigma current_value")
        #print("-exit bartpy/bartpy/sigma.py Sigma current_value")
        return self._current_value

    def current_unnormalized_value(self) -> float:
        #print("enter bartpy/bartpy/sigma.py Sigma current_value")
        output = self.current_value() * self.scaling_factor
        #print("-exit bartpy/bartpy/sigma.py Sigma current_value")
        return output
