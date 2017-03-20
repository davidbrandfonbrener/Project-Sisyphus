import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
import backend as B


def set_params(n_in = 2, input_wait = 3, mem_gap = 4, stim_dur = 3, out_dur=5,
                    var_delay_length = 0, stim_noise = 0, rec_noise = .1,
                    sample_size = 128, epochs = 100, N_rec = 50, dale_ratio=0.8, tau=100):
    params = dict()
    params['n_in']          = n_in
    params['input_wait']       = input_wait
    params['mem_gap']        = mem_gap
    params['stim_dur']         = stim_dur
    params['out_dur']           = out_dur
    params['var_delay_length'] = var_delay_length
    params['stim_noise']       = stim_noise
    params['rec_noise']        = rec_noise
    params['sample_size']      = sample_size
    params['epochs']           = epochs
    params['N_rec']            = N_rec
    params['dale_ratio']       = dale_ratio
    params['tau'] = tau

    return params

# This generates the training data for our network
# It will be a set of input_times and output_times for when we expect input
# and when the corresponding output is expected
def build_train_trials(params):
    n_in = params['n_in']
    input_wait = params['input_wait']
    mem_gap = params['mem_gap']
    stim_dur = params['stim_dur']
    out_dur = params['out_dur']
    var_delay_length = params['var_delay_length']
    stim_noise = params['stim_noise']
    sample_size = int(params['sample_size'])

    if var_delay_length == 0:
        var_delay = np.zeros(sample_size, dtype=int)
    else:
        var_delay = np.random.randint(var_delay_length, size=sample_size) + 1

    seq_dur = input_wait + stim_dur + mem_gap + stim_dur + out_dur

    input_pattern = np.random.randint(2,size=(sample_size,2))
    #output_pattern = (np.sum(input_pattern,1) >= 1).astype('float') #or
    #output_pattern = (np.sum(input_pattern,1) >= 2).astype('float') #and
    output_pattern = (np.sum(input_pattern,1) == 1).astype('float') #xor
    #output_pattern = input_pattern[:,0]                             #memory saccade with distractor

    input_times = np.zeros([sample_size, n_in], dtype=np.int)
    output_times = np.zeros([sample_size, 1], dtype=np.int)


    x_train = np.zeros([sample_size, seq_dur, 2])
    y_train = 0.5 * np.ones([sample_size, seq_dur, 1])
    for sample in np.arange(sample_size):

        in_period1 = range(input_wait,(input_wait+stim_dur))
        in_period2 = range(input_wait+stim_dur+mem_gap,(input_wait+stim_dur+mem_gap+stim_dur))
        x_train[sample,in_period1,0] = input_pattern[sample,0]
        x_train[sample,in_period2,1] = input_pattern[sample,1]
        
        out_period = range(input_wait+stim_dur+mem_gap+stim_dur,input_wait+stim_dur+mem_gap+stim_dur+out_dur)
        y_train[sample,out_period,0] = output_pattern[sample]

    #note:#TODO im doing a quick fix, only considering 1 ouput neuron
    mask = np.ones((sample_size, seq_dur, 1))
    #for sample in np.arange(sample_size):
    #    mask[sample, :, 0] = [0.0 if x == .5 else 1.0 for x in y_train[sample, :, :]]
    #mask = np.array(mask, dtype=float)

    x_train = x_train + stim_noise * np.random.randn(sample_size, seq_dur, 2)
    params['input_times'] = input_times
    params['output_times'] = output_times
    return x_train, y_train, mask

def generate_train_trials(params):
    while 1 > 0:
        yield build_train_trials(params)

        
if __name__ == "__main__":
    
    #model params
    n_in = 2 
    n_hidden = 100 
    n_out = 1
    n_steps = 80 
    tau = 100.0 #As double
    dt = 20.0  #As double
    dale_ratio = 0
    rec_noise = 0.00001
    stim_noise = 0.2
    batch_size = 128
    
    #train params
    learning_rate = .01 
    training_iters = 200000
    display_step = 50
    
    params = set_params(epochs=200, sample_size= batch_size, input_wait=10, stim_dur=10, mem_gap=20, out_dur=30, N_rec=n_hidden, 
                        rec_noise=rec_noise, stim_noise=stim_noise, dale_ratio=dale_ratio, tau=tau)
    generator = generate_train_trials(params)
    model = B.Model(n_in, n_hidden, n_out, n_steps, tau, dt, dale_ratio, rec_noise, batch_size)
    sess = tf.Session()
    
    
    
    B.train(sess, model, generator, learning_rate, training_iters, batch_size, display_step,dale_ratio)

    input,target,m = generator.next()
    output,states = B.test(sess, model, input)
    W = model.W.eval(session=sess)
    U = model.U.eval(session=sess)
    Z = model.Z.eval(session=sess)
    brec = model.brec.eval(session=sess)
    bout = model.bout.eval(session=sess)
    
    sess.close()



