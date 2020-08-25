# Estimator
This module wraps the Neural Network which is used for the cardinality estimation. For every QuerySet there should be a new Estimator isntance.

## Usage
Normally this submodule is called from `main.py`, however you may want to use it separately:

1. You need a configuration file or dict for the NN. This should look like the following:
    ```
    # Neural Network
    layer:
      - 512
      - 256
    loss_function: q_loss
    dropout: 0.2
    learning_rate: 0.0001
    kernel_initializer: normal
    activation_strategy: relu
    len_input:
    ```
    
    It contains information about the layers of the NN. You can add more (fully-connected) layers here. 
    
    The len_input can be given, but is optional. If not given, this value is calculated from the data.

2. You need a file containing the vectorized queries:
    ```
       1,0,0,1,0,0,1,0.946902654867256666,0,1,0,0.554621848739495826,134163798,0.651576470484740322,0.745803338052605902
       0,0,1,0.5,1,0,0,0.707964601769911495,1,0,1,0.0714285714285714246,134163798,0.552436280887511844,0.387697419969840307
       1,0,1,0.5,1,1,0,0.548672566371681381,1,0,1,0.911764705882352922,134163798,0.9658556575333751,0.981214080678194711
       0,1,1,1,0,1,0,0.39823008849557523,1,0,0,0.260504201680672287,134163798,0.715437781548679874,0.651506384900475854
       0,0,1,1,1,0,1,0.283185840707964598,1,0,1,0.172268907563025209,134163798,0.767619189647782418,0.7410491653476593
       0,1,1,1,1,0,0,0.477876106194690287,1,0,1,0.924369747899159711,134163798,0.973278750577822982,0.920647733098342469
       1,0,1,1,0,1,1,0.336283185840707988,1,0,0,0.0798319327731092376,134163798,0.314815867372580604,0.418093768713123426
       0,0,1,1,1,0,1,0.584070796460177011,0,0,1,0.626050420168067223,134163798,0.569767811257714807,0.141016173481957524
    ```
    
    Where the last three values must be the maximum cardinality for the QuerySet, the normalized estimated cardinality and normalized true cardinality (in this order).
    This file could either be a .csv or a .npy file with this format.
    
3. You can train the NN on this data and save it afterwards to file for reusage. 

4. The trained NN should now be capable of estimating cardinalities for the given QuerySet.