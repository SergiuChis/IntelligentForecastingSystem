import torch
from torch import optim
from torch import nn
from tqdm import tqdm
import matplotlib.pyplot as plt
from PIL import Image
from time import gmtime

from Prediction.Loaders.ImageDataLoader import *


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

    def train(self):
        loss_list = []
        expected_list = []
        result_list = []
        for i in range(self.num_epochs):
            iteration_nr = 0
            for sample in self.train_dataset:
                iteration_nr += 1
                input_sequence = torch.tensor(np.array(sample[0]), dtype=torch.float).to(self.device)
                output_expected = torch.tensor([[sample[1]]], dtype=torch.float).to(self.device)

                output = self.model(input_sequence)
                loss = self.criterion(output, output_expected)

                self.optimizer.zero_grad()
                loss.backward()
                self.optimizer.step()

                expected = output_expected[0][0].to("cpu").detach().numpy()
                predicted = output[0].to("cpu").detach().numpy()
                loss_list.append(loss.item())
                expected_list.append(expected)
                result_list.append(predicted)
                print(f"epoch: {i}, loss: {loss.item()}")
                print(f"Expected: {output_expected[0][0]}, Result: {output[0]}")
                print("------------------------------------")

                # if iteration_nr >= 300:
                #     break

        torch.save(self.model.state_dict(), self.data_paths["trained_model"])
        fig, (ax1, ax2) = plt.subplots(2, 1)
        ax1.plot(range(len(loss_list)), loss_list, color="red")
        ax2.plot(range(len(expected_list)), expected_list, color="blue")
        ax2.plot(range(len(result_list)), result_list, color="green")
        plt.show()

    def load_saved_model(self, path):
        self.model.load_state_dict(torch.load(path, map_location=torch.device("cpu")))
        self.model.eval()

    def predict(self):
        current_date = gmtime()
        sequence = self.train_dataset.get_dataset_by_date(current_date)
        # print(sequence)
        input_sequence = torch.tensor(np.array(sequence), dtype=torch.float).to(self.device)
        # print(input_sequence.shape)
        output = self.model(input_sequence)
        return output

    def test(self):
        deviation_list = []
        for sample in self.train_dataset:
            input_sequence = torch.tensor(np.array(sample[0]), dtype=torch.float).to(self.device)
            output_expected = torch.tensor([[sample[1]]], dtype=torch.float).to(self.device)

            output = self.model(input_sequence)

            expected = output_expected[0][0].to("cpu").detach().numpy()
            predicted = output[0].to("cpu").detach().numpy()

            deviation_list.append(abs(expected - predicted))
        return mean(deviation_list)

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

    @staticmethod
    def __get_prediction_number(tensor):
        return torch.argmax(tensor).item() + 1


# TODO testeaza si alte optimizers
# TODO mecanism de early stopping
# TODO prezic una din cele 4 valori
# TODO mai multe imagini in secventa
# TODO impartim sunny vallue in 4 clustere
