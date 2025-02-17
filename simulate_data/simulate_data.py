import numpy as np
import pandas as pd
from scipy.stats import norm
from scipy.special import logit, expit


def get_data(data, n, add_prop_score=0):
    X = data["X"]
    pi=data["p"]
    if add_prop_score == 1:
        X=np.concatenate([X, pi.reshape(n,1)], axis=1)
    return data["Y"], data["W"], X, data["tau"], pi


def inv_log_odds(LO):
    """
    args: LO , float or list of floats: representing Log Odds
    returns inverse logit of LO
    """
    return 1/(1+ (np.exp(np.array(-LO))))


def get_Y_obs(Y0_given_X, Y1_given_X, W_i):
    
    Y0_given_X = np.array(Y0_given_X)
    Y1_given_X = np.array(Y1_given_X)
    W_i = np.array(W_i)
    
    Y_obs = Y0_given_X
    Y_obs[W_i == 1] = Y1_given_X[W_i == 1]
    
    return Y_obs


def get_Y_i_star(Y_obs, W_i, p):
    Y_obs = np.array(Y_obs)
    W_i = np.array(W_i)
    p = np.array(p)
    return Y_obs * (W_i - p)/(p*(1-p))


def get_variance_Y_i_star(var_1, var_0,p,mu_1,mu_0):
    var_1=np.array(var_1)
    var_0=np.array(var_0)
    p=np.array(p)
    mu_1=np.array(mu_1)
    mu_0=np.array(mu_0)
    
    odds=p/(1-p)
    output = (
        var_1/(p*(1-p)) +
        (var_0 - var_1)/(1-p) + 
        odds*mu_0*mu_0 +
        (1/odds)*mu_1*mu_1 + 
        2*mu_0*mu_1
    )
    return output


def get_Y_i_star_tilda(Y_i_star, std_Y_i_star):
    return np.array(Y_i_star)/np.array(std_Y_i_star)


def make_basic_linear_data(p, N, y_0_1_noise_scale=0.0001, log_odds_noise_scale=0.0001, random_seed = 58):

    """
    returns: basic_linear_data, lm_true_beta_propensity_scores, lm_true_beta_response
    """
    np.random.seed(seed=random_seed)

    basic_linear_data = pd.DataFrame(np.random.uniform(low=-1, high=1, size=(N,p-1)),
                         columns=list("V."+pd.Series(list(range(1,p))).apply(str))
                        )
    basic_linear_data["V.0"] = 1
    predictor_columns = list("V."+pd.Series(list(range(0,p))).apply(str))

    basic_linear_data = basic_linear_data[predictor_columns]

    lm_true_beta_propensity_scores = np.random.uniform(low=-1, high=1, size=p)
    lm_true_beta_response = np.random.uniform(low=-1, high=1, size=p)
    lm_true_beta_treatment = np.random.uniform(low=-1, high=1, size=p)
    
    mu_0 = np.matmul(basic_linear_data[predictor_columns].to_numpy(), lm_true_beta_response) 
    basic_linear_data["Y0_given_X"] = (
        mu_0 + np.random.normal(loc=0, scale=y_0_1_noise_scale, size=basic_linear_data.shape[0])
    )
    mu_1 = mu_0 + np.matmul(basic_linear_data[predictor_columns].to_numpy(), lm_true_beta_treatment)
    basic_linear_data["Y1_given_X"]  = (
        basic_linear_data["Y0_given_X"] + np.matmul(basic_linear_data[predictor_columns].to_numpy(), lm_true_beta_treatment)
        #np.random.normal(loc=treatment_effect, scale=treatment_effect_noise, size = basic_linear_data.shape[0])
    )
    basic_linear_data["Tau"] = basic_linear_data["Y1_given_X"]-basic_linear_data["Y0_given_X"]
    
    log_odds = (
        np.matmul(basic_linear_data[predictor_columns].to_numpy(), lm_true_beta_propensity_scores) + 
        np.random.normal(loc=0, scale=log_odds_noise_scale, size=basic_linear_data.shape[0])
    )
    
    p=inv_log_odds(log_odds)
    basic_linear_data["P(T=1)"] = p
    basic_linear_data["T"] = np.random.binomial(n=1, p=basic_linear_data["P(T=1)"])
    
    
    basic_linear_data["Y_obs"] = get_Y_obs(
        basic_linear_data["Y0_given_X"], basic_linear_data["Y1_given_X"], basic_linear_data["T"])
    
    basic_linear_data["mu_0"] = mu_0
    basic_linear_data["mu_1"] = mu_1
    basic_linear_data["var_1"] = y_0_1_noise_scale*y_0_1_noise_scale
    
    var_1 = var_0 = y_0_1_noise_scale*y_0_1_noise_scale
    
    basic_linear_data["Var(Y_i_star)_true"] = get_variance_Y_i_star(var_1, var_0,p,mu_1,mu_0)
    
    basic_linear_data["Y_i_star_true"] = get_Y_i_star(basic_linear_data["Y_obs"], basic_linear_data["T"], p)
    
    basic_linear_data["Y_i_star_tilda_true"] = get_Y_i_star_tilda(
        basic_linear_data["Y_i_star_true"], np.sqrt(np.array(basic_linear_data["Var(Y_i_star)_true"])))
    
    return basic_linear_data, lm_true_beta_propensity_scores, lm_true_beta_response, predictor_columns


def make_hahn_data(function_type="linear", effect_type="heterogeneous", n_in_study=500, seed=0):
# Five variables comprise x; the first three are continuous, drawn as standard normal random variables, the fourth is a dichotomous variable and the fifth is unordered categorical, taking three levels (denoted 1, 2, 3).
    
    np.random.seed(seed)
    
    def g(x):
        # g(1) = 2, g(2) = −1 and g(3) = −4
        return -2*x+5
    
    x_1 = np.random.normal(loc=0, scale=1, size=n_in_study)
    x_2 = np.random.normal(loc=0, scale=1, size=n_in_study)
    x_3 = np.random.normal(loc=0, scale=1, size=n_in_study)
    x_4 = np.random.choice([1,2,3], size=n_in_study)
    x_5 = np.random.binomial(n=1,p=.5, size=n_in_study)
    
    if effect_type == "homogeneous":
        # τ(x) = 3, homogeneous
        Tau=3
    if effect_type == "heterogeneous":
        # τ(x) = 1 + 2*x_2*x_5, heterogeneous,
        Tau = 1 + 2*x_2*x_5
    
    if function_type == "linear":
        # μ(x) = 1 + g(x4) + x1x3, linear,
        mu = 1 + g(x_4) + x_1*x_3
    if function_type == "nonlinear":
        # μ(x) = −6 + g(x4) + 6|x3 − 1|, nonlinear,
        mu = -6 + g(x_4) + 6*np.absolute(x_3 - 1)
    # the propensity function is π(xi) = 0.8*Φ(3*μ(x_i)/s − 0.5*x_1) + 0.05 + u_i/10,
    # where s is the standard deviation of μ taken over the observed sample and u_i ∼ Uniform(0, 1).
    s = np.std(mu)
    u_i=np.random.uniform(size=n_in_study)
    pi = 0.8*norm.cdf(3*mu/s - 0.5*x_1) + 0.05 + u_i/10
    w_i = np.random.binomial(n=1,p=pi, size=n_in_study)
    
    dummies = pd.get_dummies(x_4)
    dummies.columns = ["x_4_" + i for i in dummies.columns.values.astype(str)] 

    output=pd.DataFrame(
        {
            "X0":1,
            "X1":x_1,
            "X2":x_2,
            "X3":x_3,
            "X4":x_4,
            "X5":x_5,
            "W":w_i,
            "tau":Tau,
            "p":pi,
            "X1_X3":x_1*x_3,
            "X2_X5":x_2*x_5,
            "X4_1": dummies.x_4_1, "X4_2": dummies.x_4_2, "X4_3": dummies.x_4_3,
            "Y0": mu,
            "Y1": mu+Tau,
            "Y":mu+Tau*w_i,
        }
    )
    return output


def make_zaidi_data_A(n=250, seed=0, variance=0.0001):

    # data
    np.random.seed(seed)

    X_1_15  = np.random.normal(loc=0, scale=1, size=(250,15))
    X_16_30 = np.random.uniform(low=0,high=1, size=(250,15))
    p_k = expit(X_1_15[:,:5] - X_16_30[:,:5])
    X_31_35 = np.random.binomial(n=1, p=p_k)
    lambda_k = 5 + 0.75 * X_1_15[:,:5] * (X_16_30[:,:5] + X_31_35)
    X_36_40 = np.random.poisson(lam=lambda_k)
    X=np.concatenate([X_1_15, X_16_30, X_31_35, X_36_40], axis=1)
    
    # propensity scores
    true_pi = expit(
        .3*np.sum(X_1_15[:,:5], axis=1) - 
        .5*np.sum(X_16_30[:,6:11], axis=1) - 
        .0001 * (np.sum(X_16_30[:,-5:], axis=1) + np.sum(X_31_35, axis=1)) +
        .055 * np.sum(X_36_40, axis=1)
    )
    Xp=np.concatenate(
        [
            X_1_15, 
            X_16_30, 
            X_31_35, 
            X_36_40, 
            np.reshape(true_pi, (len(true_pi),1))
        ], 
        axis=1
    )
    
    W = np.random.binomial(n=1, p=true_pi)
    
    # potential outcomes
    error_0 = np.random.normal(0, np.sqrt(variance), size=n)
    error_1 = np.random.normal(0, np.sqrt(variance), size=n)
    
    term = (
        X_16_30[:,0] * np.exp(np.reshape(X_16_30[:,-1:], n)) + 
        X_16_30[:,1] * np.exp(np.reshape(X_31_35[:,0], n)) + 
        X_16_30[:,2] * np.exp(np.reshape(X_31_35[:,1], n)) + 
        X_16_30[:,3] * np.exp(np.reshape(X_31_35[:,2], n)) 
    )
    f_of_X = term/(1+term)

    f0=0.15 * np.sum(X_1_15[:,:5], axis=1) + 1.5 * np.exp( 1 + 1.5*f_of_X )
    f1=(
        np.sum(
            2.15*X_1_15[:,:5] + 
            2.75*X_1_15[:,:5]*X_1_15[:,:5] + 
            10 * X_1_15[:,:5]*X_1_15[:,:5]*X_1_15[:,:5],
            axis=1
        ) + 
        1.25*np.sqrt(.5 + 1.5*np.sum(X_36_40, axis=1))
    )
    
    Y0 = f0 + error_0
    Y1 = f1 + error_1
    
    tau = f1-f0
    h = f1/true_pi  + f0/(1-true_pi)
    
    Y = W*Y1 + (1-W)*Y0
    Xy = np.concatenate([X_1_15[:,:5], X_16_30[:,0:4], X_16_30[:,-1:], X_31_35[:,0:3], X_36_40],axis=1)
    return {
        "X":X, "Xp":Xp, "Xy":Xy, "Y":Y, "W":W, "p":true_pi, "tau":tau, "Y1":Y1, "Y0":Y0, "h(x)":h
    }


def make_zaidi_data_B(n_in_study=250, seed=0, variance=0.0001):
    np.random.seed(seed)

    def h(x):
        # g(0) = 2, g(1) = −1 and g(2) = −4
        return -3*x+2
    
    # the data
    X_1_3 = np.random.normal(loc=0, scale=1, size=(n_in_study, 3))
    X_4 = np.random.binomial(n=1, p=0.25, size = n_in_study)
    X_5 = np.random.binomial(n=2, p=0.5, size = n_in_study)
    
    # the intervention
    true_pi = expit(0.1*X_1_3[:,0] - 0.001*X_1_3[:,1] + .275*X_1_3[:,2] - 0.03*X_4)
    W = np.random.binomial(n=1, p=true_pi, size = n_in_study)
    
    # outcomes
    f_of_X = -6 + h(X_5) + np.absolute(X_1_3[:,2] - 1)
    error_0 = np.random.normal(loc=0, scale=np.sqrt(variance), size = n_in_study)
    error_1 = np.random.normal(loc=0, scale=np.sqrt(variance), size = n_in_study)
    
    f0 = f_of_X - 15*X_1_3[:,2]
    f1 = f_of_X + (1 + 2*X_1_3[:,1]*X_1_3[:,2])
    
    Y0 = f0 + error_0
    Y1 = f1 + error_1
    
    tau = f1 - f0
    h = f1/true_pi  + f0/(1-true_pi)
    
    Y = W*Y1 + (1-W)*Y0
    
    X=np.concatenate([X_1_3, X_4.reshape((n_in_study,1)), X_5.reshape((n_in_study,1))], axis=1)
    
    return {
        "X":X, "Y":Y, "W":W, "p":true_pi, "tau":tau, "Y1":Y1, "Y0":Y0, "h(x)":h,
    }


def make_CMM_data_A(n, per_var, seed):
    """
    n (int): number of observations
    per_var (float): percent of g's variation = model std dev.
    seed (int): seed for random number generator
    """
    np.random.seed(seed)
    X = np.random.uniform(low=-3,high=3, size=(n,3))

    f0 = X[:,1]**2
    f1 = X[:,1]**2 + np.abs(X[:,2])

    pi = expit(X[:,0])#np.ones(n)*0.5#expit(X[:,0])
    h = f1/pi + f0/(1-pi)
    g = tau = f1-f0
    #print("Var(g):",np.var(g))
    #print("Var(h):",np.var(h))
    max_val = np.var(g)#np.max((np.var(g),np.var(h)))
    
    sig = np.sqrt(max_val*per_var)
    #print("sig=", sig)
    sig0_star = sig/(1-pi)
    sig1_star = sig/pi

    error0_star = -pi*h    + np.random.normal(loc=0, scale = sig0_star)
    error1_star = (1-pi)*h + np.random.normal(loc=0, scale = sig1_star)

    W = np.random.binomial(n=1, p=pi)

    Y0 = -(1-pi)*(g+error0_star)
    Y1 = pi*(g+error1_star)
    
    Y_obs = np.zeros(n)
    Y_obs[W==0] = Y0[W==0]
    Y_obs[W==1] = Y1[W==1]

    y_i_star = np.zeros(n)
    y_i_star[W==0] = (g + error0_star)[W==0]
    y_i_star[W==1] = (g + error1_star)[W==1]

    output = {
        'X':X,
        'Y_obs':Y_obs,
        'Y1':Y1,
        'Y0':Y0,
        'f1':f1,
        'f0':f0,
        "Y_i_star":y_i_star,
        'g(x)':g,
        'h(x)':h,
        'p':pi,
        'W':W,
        'sig':sig,
    }
    return output


def make_CMM_data_B(n, per_var, seed):
    """
    n (int): number of observations
    per_var (float): percent of g's variation = model std dev.
    seed (int): seed for random number generator
    """
    np.random.seed(seed)
    X = np.random.uniform(low=-3,high=3, size=(n,3))

    f0 = X[:,1]**2
    f1 = X[:,1]**2 + np.abs(X[:,2])

    pi = expit(X[:,0])#np.ones(n)*0.5#expit(X[:,0])
    h = f1/pi + f0/(1-pi)
    g = tau = f1-f0
    #print("Var(g):",np.var(g))
    #print("Var(h):",np.var(h))
    max_val = np.var(g)#np.max((np.var(g),np.var(h)))
    
    sig = np.sqrt(max_val*per_var)
    #print("sig=", sig)
    sig0_star = sig/(1-pi)
    sig1_star = sig/pi

    error0_star = -pi*h    + np.random.normal(loc=0, scale = sig0_star)
    error1_star = (1-pi)*h + np.random.normal(loc=0, scale = sig1_star)

    W = np.random.binomial(n=1, p=pi)

    Y0 = -(1-pi)*(g+error0_star)
    Y1 = pi*(g+error1_star)
    
    Y_obs = np.zeros(n)
    Y_obs[W==0] = Y0[W==0]
    Y_obs[W==1] = Y1[W==1]

    y_i_star = np.zeros(n)
    y_i_star[W==0] = (g + error0_star)[W==0]
    y_i_star[W==1] = (g + error1_star)[W==1]

    output = {
        'X':X,
        'Y_obs':Y_obs,
        'Y1':Y1,
        'Y0':Y0,
        'f1':f1,
        'f0':f0,
        "Y_i_star":y_i_star,
        'g(x)':g,
        'h(x)':h,
        'p':pi,
        'W':W,
        'sig':sig,
    }
    return output
    
    
def get_posterior_samples_data(stem,nreps,nsamp,nburn,ntree,nchain,thin,alpha,beta,k):
    name = (
    stem +
    "_n_replications="+ str(nreps) +
    "_n_samples=" + str(nsamp) +
    "_n_burn=" + str(nburn) + 
    "_n_trees=" + str(ntree) +
    "_n_chains=" + str(nchain) + 
    "_thin=" + str(thin) + 
    "_alpha=" + str(alpha) + 
    "_beta=" + str(beta) + 
    "_k=" + str(k) + ".npy"
    )
    return np.load(name)   
    

def make_CMM_data_C(n, per_var, seed):
    """
    n (int): number of observations
    per_var (float): percent of g's variation = model std dev.
    seed (int): seed for random number generator
    """
    np.random.seed(seed)
    X = np.random.uniform(low=-3,high=3, size=(n,1))

    pi = expit(X[:,0])#np.ones(n)*0.5#expit(X[:,0])
    
    f0 = 1 - pi
    f1 = pi

    
    h = f1/pi + f0/(1-pi)
    g = tau = f1-f0
    #print("Var(g):",np.var(g))
    #print("Var(h):",np.var(h))
    max_val = np.var(g)#np.max((np.var(g),np.var(h)))
    
    sig = np.sqrt(max_val*per_var)
    #print("sig=", sig)
    sig0_star = sig/(1-pi)
    sig1_star = sig/pi

    error0_star = -pi*h    + np.random.normal(loc=0, scale = sig0_star)
    error1_star = (1-pi)*h + np.random.normal(loc=0, scale = sig1_star)

    W = np.random.binomial(n=1, p=pi)

    Y0 = -(1-pi)*(g+error0_star)
    Y1 = pi*(g+error1_star)
    
    Y_obs = np.zeros(n)
    Y_obs[W==0] = Y0[W==0]
    Y_obs[W==1] = Y1[W==1]

    y_i_star = np.zeros(n)
    y_i_star[W==0] = (g + error0_star)[W==0]
    y_i_star[W==1] = (g + error1_star)[W==1]

    output = {
        'X':X,
        'Y_obs':Y_obs,
        'Y1':Y1,
        'Y0':Y0,
        'f1':f1,
        'f0':f0,
        "Y_i_star":y_i_star,
        'g(x)':g,
        'h(x)':h,
        'p':pi,
        'W':W,
        'sig':sig,
    }
    return output


def get_posterior_samples_data_2(stem,nreps,nsamp,nburn,ntreeh,ntreeg,nchain,thin,alpha,beta,k):
    name = (
    stem +
    "_n_replications="+ str(nreps) +
    "_n_samples=" + str(nsamp) +
    "_n_burn=" + str(nburn) + 
    "_n_trees_h=" + str(ntreeh) +
    "_n_trees_g=" + str(ntreeg) +
    "_n_chains=" + str(nchain) + 
    "_thin=" + str(thin) + 
    "_alpha=" + str(alpha) + 
    "_beta=" + str(beta) + 
    "_k=" + str(k) + ".npy"
    )
    return np.load(name)


def CBARTMM_likelihood(resp, W,p,g,h,sigma):
    n=len(p)
    i_factor = W/p + (1-W)/(1-p)
    mu_i = g + (W*(1-p) - (1-W)*p)*h
    sigma_i = sigma*i_factor
    LL = -(n*.5)*np.log(2*np.pi)  - np.sum(np.log(sigma_i)) - 0.5*np.sum( ( (resp-mu_i)/sigma_i)**2 )
    return LL
    
    
def BART_normalize_values(y):
    y_min, y_max = np.min(y), np.max(y)
    output = -0.5 + ((y - y_min) / (y_max - y_min))
    return output