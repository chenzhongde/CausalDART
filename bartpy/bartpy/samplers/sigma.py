import numpy as np

from bartpy.bartpy.model import Model, ModelCGM
from bartpy.bartpy.samplers.sampler import Sampler
from bartpy.bartpy.sigma import Sigma


class SigmaSampler(Sampler):

    def step(self, model: Model, sigma: Sigma) -> float:
        #print("enter bartpy/bartpy/samplers/sigma.py SigmaSampler step")
        sample_value = self.sample(model, sigma)
        sigma.set_value(sample_value)
        #print("-exit bartpy/bartpy/samplers/sigma.py SigmaSampler step")
        return sample_value
    
    def step_cgm(self, model: ModelCGM, sigma: Sigma) -> float:
        #print("enter bartpy/bartpy/samplers/sigma.py SigmaSampler step_cgm")
        if model.fix_sigma is None:
            sample_value = self.sample_cgm(model, sigma)
            sigma.set_value(sample_value)
        else:
            sample_value = model.fix_sigma
            sigma.set_value(model.fix_sigma)
        #print("-exit bartpy/bartpy/samplers/sigma.py SigmaSampler step_cgm")
        return sample_value
    
    def step_cgm_g(self, model: ModelCGM, sigma: Sigma) -> float:
        #print("enter bartpy/bartpy/samplers/sigma.py SigmaSampler step_cgm_g")
        sample_value = self.sample_cgm_g(model, sigma)
        sigma.set_value(sample_value)
        #print("-exit bartpy/bartpy/samplers/sigma.py SigmaSampler step_cgm_g")
        return sample_value
    
    def step_cgm_h(self, model: ModelCGM, sigma: Sigma) -> float:
        #print("enter bartpy/bartpy/samplers/sigma.py SigmaSampler step_cgm_h")
        sample_value = self.sample_cgm_h(model, sigma)
        sigma.set_value(sample_value)
        #print("-exit bartpy/bartpy/samplers/sigma.py SigmaSampler step_cgm_h")
        return sample_value

    @staticmethod
    def sample(model: Model, sigma: Sigma) -> float:
        #print("enter bartpy/bartpy/samplers/sigma.py SigmaSampler sample")
        posterior_alpha = sigma.alpha + (model.data.X.n_obsv / 2.)
        posterior_beta = sigma.beta + (0.5 * (np.sum(np.square(model.residuals()))))
        draw = np.power(np.random.gamma(posterior_alpha, 1./posterior_beta), -0.5)
        #print("-exit bartpy/bartpy/samplers/sigma.py SigmaSampler sample")
        return draw

    @staticmethod
    def sample_cgm(model: ModelCGM, sigma: Sigma) -> float:
        #print("enter bartpy/bartpy/samplers/sigma.py SigmaSampler sample_cgm")
        paw2 = model.data.W.values*(model.data.p.values**2) + (1-model.data.W.values)*((1-model.data.p.values)**2)
        posterior_alpha = sigma.alpha + (model.data.X.n_obsv / 2.)
        posterior_beta = sigma.beta + (0.5 * (np.sum(paw2*np.square(model.residuals()))))
        #print("posterior_alpha=",posterior_alpha)
        #print("posterior_beta=",posterior_beta)
        draw = np.power(np.random.gamma(posterior_alpha, 1./posterior_beta), -0.5)
        #print("-exit bartpy/bartpy/samplers/sigma.py SigmaSampler sample_cgm")
        return draw
    
    #@staticmethod
    #def sample_cgm_g(model: ModelCGM, sigma: Sigma) -> float:
    #    #print("enter bartpy/bartpy/samplers/sigma.py SigmaSampler sample_cgm_g")
    #    posterior_alpha = sigma.alpha + (model.data.X.n_obsv / 2.)
    #    posterior_beta = sigma.beta + (0.5 * (np.sum(np.square(model.residuals_g()))))
    #    draw = np.power(np.random.gamma(posterior_alpha, 1./posterior_beta), -0.5)
    #    #print("-exit bartpy/bartpy/samplers/sigma.py SigmaSampler sample_cgm_g")
    #    return draw
    #
    #@staticmethod
    #def sample_cgm_h(model: ModelCGM, sigma: Sigma) -> float:
    #    #print("enter bartpy/bartpy/samplers/sigma.py SigmaSampler sample_cgm_h")
    #    posterior_alpha = sigma.alpha + (model.data.X.n_obsv / 2.)
    #    posterior_beta = sigma.beta + (0.5 * (np.sum(np.square(model.residuals_h()))))
    #    draw = np.power(np.random.gamma(posterior_alpha, 1./posterior_beta), -0.5)
    #    #print("-exit bartpy/bartpy/samplers/sigma.py SigmaSampler sample_cgm_h")
    #    return draw