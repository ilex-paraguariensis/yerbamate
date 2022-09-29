import torch
import ipdb


class Optimizer:
    def __init__(self, params, model):
        self.params = params
        self.model = model
        # self.__init_optimizer()
        # self.__init_lr_scheduler()

    @staticmethod
    def optimizers(params, lightning_module):

        results = []
        for model_name, optimizer_param in params.items():
            optimizer_module = __import__(optimizer_param["optimizer"]["module"], fromlist=[
                optimizer_param["optimizer"]["class"]])
            optimizer_class = getattr(
                optimizer_module, optimizer_param["optimizer"]["class"])

            model_params = getattr(lightning_module, model_name).parameters()
            optimizer = optimizer_class(
                params=model_params, **optimizer_param["optimizer"]["params"])

            result = {
                "optimizer": optimizer,
            }

            if "lr_scheduler" in optimizer_param:
                lr_scheduler_module = __import__(optimizer_param["lr_scheduler"]["scheduler"]["module"], fromlist=[
                    optimizer_param["lr_scheduler"]["scheduler"]["class"]])
                lr_scheduler_class = getattr(
                    lr_scheduler_module, optimizer_param["lr_scheduler"]["scheduler"]["class"])

                lr_scheduler = lr_scheduler_class(
                    optimizer=optimizer, **optimizer_param["lr_scheduler"]["scheduler"]["params"])

                remaining_args = optimizer_param["lr_scheduler"].copy()
                del remaining_args["scheduler"]

                result["lr_scheduler"] = {
                    "scheduler": lr_scheduler,
                }
                result["lr_scheduler"].update(remaining_args)
            results.append(result)

        if len(results) == 1:
            return results[0]
        return results

    @staticmethod
    def __params_to_object(module, params):
        params_without_type = {
            key: val for key, val in params.items() if key != "type"
        }
        return getattr(module, params["type"])(**params_without_type)

    def __call__(self):
        if "type" in self.params:
            return self.__params_to_object(
                torch.optim, self.params | {"params": self.model.parameters()}
            )
        else:
            result = self.params.clone()
            result["optimizer"] = self.__params_to_object(
                torch.optim,
                self.params.optimizer | {"params": self.model.parameters()},
            )
            result["lr_scheduler"]["scheduler"] = self.__params_to_object(
                torch.optim.lr_scheduler,
                self.params.lr_scheduler.scheduler
                | {"optimizer": result.optimizer},
            )
            return result

    '''
    def __init_optimizer(self):
        params_without_type_and_scheduler = {
            key: val
            for key, val in self.optim_params.items()
            if key != "type" and key != "lr_scheduler"
        }

        """
        if self.params.type == "sgd":
            self.optimizer = torch.optim.SGD(
                self.model.parameters(),
                lr=self.params.lr,
                momentum=self.params.momentum,
            )

        elif self.params.type == "adam":
            self.optimizer = torch.optim.Adam(
                self.model.parameters(),
                lr=self.params.lr,
                betas=(self.params.beta1, self.params.beta2),
            )
        """
        self.optimizer = torch.optim.__dict__[self.optim_params.type](
            self.model.parameters(), **params_without_type_and_scheduler
        )

    def __init_lr_scheduler(self):
        params_without_type_and_monitor = {
            key: val
            for key, val in self.lr_params.scheduler.items()
            if key != "type"
        }
        self.lr_scheduler = torch.optim.lr_scheduler.__dict__[
            self.lr_params.scheduler.type
        ](self.optimizer, **params_without_type_and_monitor)
        """
        if self.params.lr_scheduler == None:
            return
        if self.params.lr_scheduler.type == "step":
            self.lr_scheduler = torch.optim.lr_scheduler.StepLR(
                self.optimizer,
                step_size=self.params.lr_scheduler.step_size,
                gamma=self.params.lr_scheduler.gamma,
            )
        elif self.params.lr_scheduler.type == "multi_step":
            self.lr_scheduler = torch.optim.lr_scheduler.MultiStepLR(
                self.optimizer,
                milestones=self.params.lr_scheduler.milestones,
                gamma=self.params.lr_scheduler.gamma,
            )
        elif self.params.lr_scheduler.type == "exponential":
            self.lr_scheduler = torch.optim.lr_scheduler.ExponentialLR(
                self.optimizer, gamma=self.params.lr_scheduler.gamma
            )
        elif self.params.lr_scheduler.type == "cosine":
            self.lr_scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
                self.optimizer,
                T_max=self.params.lr_scheduler.T_max,
                eta_min=self.params.lr_scheduler.eta_min,
            )
        elif self.params.lr_scheduler.type == "reduce_on_plateau":
            self.lr_scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
                self.optimizer,
                mode=self.params.lr_scheduler.mode,
                factor=self.params.lr_scheduler.factor,
                patience=self.params.lr_scheduler.patience,
                verbose=self.params.lr_scheduler.verbose,
                threshold=self.params.lr_scheduler.threshold,
                threshold_mode=self.params.lr_scheduler.threshold_mode,
            )
        """
        '''
