from os import environ as ENV

import torch
from torch.optim import SGD, Adam
from torch.optim.lr_scheduler import CyclicLR, ExponentialLR
from torch.utils.tensorboard import SummaryWriter

from octLearn.autoencoder.TaskSynthesis import Features2TaskTensors, Features2ParamTensors
from octLearn.autoencoder.autoencoder import Encoder, Decoder
from octLearn.autoencoder.convnet import FlatToFlatNetwork, FlatToImgNetwork, ImgToFlatNetwork, ImgToImgDisturbNetwork
from octLearn.autoencoder.radiencoder import RateDistortionAutoencoder
from octLearn.connector.dbRecords import MongoInstance, MongoOffline
from octLearn.f.torch_dataset import HopDataset
from octLearn.g.TrainingHost import TrainingHost
from octLearn.utils import RandSeeding, WeightInitializer

# ENV['FeatRoot'] = '/path/to/features'
# ENV['TrajRoot'] = '/path/to/trajectories'
# ENV['MongoRoot'] = '/path/to/MongoDB/dumps'

EPOCH_MAX = 800
MONGO_ADAPTER = MongoInstance  # [ MongoInstance, MongoOffline ]

CUDA = "cuda:0"
CPU = "cpu"


def main():
    task_train_autoencoder = dict(device=torch.device(CUDA), latent_size=20, load_pretrained=False, model_path=None,
                               batch_size=128, num_workers=8, step_per_epoch=100, collate_fn=None)
    task_train_decipher = dict(device=torch.device(CUDA), latent_size=100, load_pretrained=True, model_path=None,
                               batch_size=128, num_workers=8, step_per_epoch=100, collate_fn=None,
                               load_pretrained_mask=(1, 1, 0))

    configs = task_train_autoencoder
    components = dict(image_preprocessor=Features2TaskTensors, param_preprocessor=Features2ParamTensors,
                      image_encoder=(Encoder, ImgToFlatNetwork),
                      image_decoder=(Decoder, FlatToImgNetwork, ImgToImgDisturbNetwork),
                      param_decipher=(FlatToFlatNetwork,),
                      autoencoder_policy=(RateDistortionAutoencoder, dict(lambda0=1, lambda1=0.001)),
                      weight_initializer=(WeightInitializer,),
                      autoencoder_optimizer=(SGD, dict(lr=0.01, weight_decay=0.002)),
                      autoencoder_lr_scheduler=(CyclicLR, dict(base_lr=0.01, max_lr=0.1, step_size_up=EPOCH_MAX // 10)),
                      decipher_optimizer=(Adam, dict(lr=0.1, weight_decay=0.002)),
                      decipher_lr_scheduler=(ExponentialLR, dict(gamma=0.98)), )

    RandSeeding()
    db = MONGO_ADAPTER('learning', 'completed')
    dataset = HopDataset(db.Case_Ids())

    trainer = TrainingHost(configs)
    trainer.build_network(dataset, **components)
    if configs['load_pretrained']:
        trainer.load(load_mask=configs['load_pretrained_mask'])

    writer = SummaryWriter()
    print("Training begin.")

    autoencoder_train(trainer, writer)
    trainer.dump()
    decipher_train(trainer, writer)
    trainer.dump()


def autoencoder_train(trainer, writer):
    train_task = trainer.autoencoder.loopTrain(writer)
    for step in range(EPOCH_MAX):
        try:
            reward = next(train_task)
            print("Train step {} ends, loss: {}".format(step, float(reward)))
        except KeyboardInterrupt:
            continue


def decipher_train(trainer, writer):
    train_task = trainer.decipher.loopTrain(writer)
    for step in range(EPOCH_MAX):
        try:
            reward = next(train_task)
            print("Train step {} ends, loss: {}".format(step, float(reward)))
        except KeyboardInterrupt:
            continue


# Disable annoying unused code truncate
# noinspection PyStatementEffect
def implicit_used():
    ENV, MongoInstance, MongoOffline


if __name__ == '__main__':
    main()