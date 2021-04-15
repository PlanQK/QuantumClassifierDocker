# Quantum GAN: Outlier Detection in a Docker Cotainer
This repository contains a semi supervised method to perform outlier detecion with a (simulated) quantum computer.
The core algorithm returns an outlier score, but a threshold of the outlier score is optimized with the labelled input.

## Prerequisites
A system running Docker.


## How to build
Run the command
```
docker build -t quantumAnomaly:1.0 .
```
This builds the docker image `qanomaly:1.0`.

## How to run
After the image was created. A container can be started by:
```
docker run \
    --mount type=bind,source=/path/to/input/data/,target=/quantum-anomaly/input-data \
    --mount type=bind,source=/path/to/save/model/,target=/quantum-anomaly/model \
    qanomaly:1.0 classical|tfqSimulator|pennylaneSimulator|pennylaneIBMQ train|predict
```
The possible backends that are currently supported are:
```
    classical: Purely classical generator using Tensorflow
    tfqSimulator: Parametrized circuit with tensorflow quantum
    pennylaneSimulator: Parametrized circuit with Pennylane
    pennylaneIBMQ: Same as pennylaneSimulator, but with the IBM Q backend
```
The container can be run in training mode by specifying the `train` flag. This will train the model and save the trained parameters in the mounted volume.
In `predict` mode the container loads the trained parameters, that were previously saved to the mounted `model` folder.

For both runs the following files need to be present in the `input-data` directory:
- `trainSet.csv`
- `predictionSet.csv`

The input data needs to be normalized and if a column called `Class` is present it will be removed, because this is an unsupervised method. For a different neural network structure the code in the file `GanClassifiers.py` needs to be adjusted.

There are many settings that can be adjusted through environment variables. Add them to the docker run command using e.g. `--env trainingSteps=100`. The following lists the settings with their default value and a short explanation.
```
    trainingSteps: 1000  Number of iteration for the training of the GAN
    latentDim: 10  size of the latent space = num qubits
    totalDepth: 4  Depth of the circuit or number of layers in the generator
    batchSize: 64  Number of samples per training step
    discriminatorIterations: 5  How often does the discriminator update its weights vs Generator
    gpWeight: 10  Weight factor for the gradient Penalty (Wasserstein Loss specific parameter)
    latentVariableOptimizationIterations: 30  Number of optimization iterations to obtain the latent variables
    ibmqx_token: ""  Token to access IBM Quantum experience
```
## Example
A sample command for a training run is therefore:
```
docker run \
    --mount type=bind,source=/path/to/input/data/,target=/quantum-anomaly/input-data \
    --mount type=bind,source=/path/to/save/model/,target=/quantum-anomaly/model \
    --env latentDim=5 --env trainingSteps=500 \
    qanomaly:1.0 classical train
```

The anomaly scores on the prediction set are then obtained by the following command:
```
docker run \
    --mount type=bind,source=/path/to/input/data/,target=/quantum-anomaly/input-data \
    --mount type=bind,source=/path/to/save/model/,target=/quantum-anomaly/model \
    --env latentDim=5 --env trainingSteps=500 \
    qanomaly:1.0 classical predict
```
Some of the environment variables change the network size and therefore must have identical values in both the training step and the prediction step. I highly encourage to keep these environment variables set between training and prediction steps, even if they might not be needed.