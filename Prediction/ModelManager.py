import torch
from torch import optim
from torch import nn
from tqdm import tqdm
import matplotlib.pyplot as plt
from PIL import Image

from Prediction.Loaders.ImageDataLoader import *
from DataGather.image_analysis import show_array_image


class ModelManager:
    def __init__(self, model, model_params, data_paths):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.input_size = model_params["input_size"]
        self.model = model(
            model_params["input_size"],
            model_params["hidden_size"],
            model_params["num_layers"],
            model_params["output_size"],
            self.device
        ).to(self.device)
        self.data_paths = data_paths
        self.train_dataset = ImageDataLoader(data_paths["geosatellite images"], device=self.device)
        self.test_dataset = None
        self.learning_rate = model_params["learning_rate"]
        self.batch_size = model_params["batch_size"]
        self.num_epochs = model_params["num_epochs"]
        self.criterion = self.__get_criterion(model_params["criterion"])
        self.optimizer = self.__get_optimizer(model_params["optimizer"])

    # def train_step(self, input_tensor_sequence, expected_output_tensor):
    #     hidden = self.model.initial_hidden()
    #     for tensor in input_tensor_sequence:
    #         output, hidden = self.model(tensor, hidden)
    #     loss = self.criterion(output, expected_output_tensor.to(self.device, dtype=torch.float))  # noqa
    #     self.optimizer.zero_grad()
    #     loss.backward()
    #     self.optimizer.step()
    #     return output, loss.item()
    #
    # def train(self):
    #     for i in range(self.num_epochs):
    #         for sample in self.train_dataset:
    #             output, loss = self.train_step(sample[0], sample[1])
    #             print(output, sample[1])
    #             print(f"loss: {loss}")

    def train(self):
        loss_list = []
        expected_list = []
        result_list = []
        for i in range(self.num_epochs):
            iteration_nr = 0
            for sample in self.train_dataset:
                iteration_nr += 1
                input_sequence = torch.tensor(np.array([sample[0]]), dtype=torch.float).to(self.device)
                output_expected = torch.tensor([[sample[1]]], dtype=torch.float).to(self.device)

                output = self.model(input_sequence)
                loss = self.criterion(output, output_expected)

                self.optimizer.zero_grad()
                loss.backward()
                self.optimizer.step()

                # loss_list.append(loss.item())
                # expected_list.append(output_expected[0][0].to("cpu").detach().numpy())
                # result_list.append(output[0][0].to("cpu").detach().numpy())
                print(f"epoch: {i}, loss: {loss.item()}")
                print(f"Expected: {output_expected[0][0]}, Result: {output[0][0]}")
                print("------------------------------------")

                # if iteration_nr >= 300:
                #     break

        plt.plot(range(len(loss_list)), loss_list, color="red")
        plt.plot(range(len(expected_list)), expected_list, color="blue")
        plt.plot(range(len(result_list)), result_list, color="green")
        plt.show()

    @staticmethod
    def __get_criterion(criterion: str):
        if criterion == "CrossEntropyLoss":
            return nn.CrossEntropyLoss()
        if criterion == "MeanSquaredErrorLoss":
            return nn.MSELoss()

    def __get_optimizer(self, optimizer: str):
        if optimizer == "Adam":
            return optim.Adam(self.model.parameters(), self.learning_rate)
        if optimizer == "SGD":
            return optim.SGD(self.model.parameters(), self.learning_rate)
        if optimizer == "Adadelta":
            return optim.Adadelta(self.model.parameters(), self.learning_rate)
        if optimizer == "AdamW":
            return optim.AdamW(self.model.parameters(), self.learning_rate)
