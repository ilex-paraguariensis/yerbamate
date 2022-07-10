import torch


class Optimizer:
    def __init__(self, params, model):
        self.params = params
        self.model = model
        self.__init_optimizer()
        self.__init_lr_scheduler()

    def get_optimizer(self):
        if self.lr_scheduler == None:
            return self.optimizer

        return {
            "optimizer": self.optimizer,
            "lr_scheduler": {
                "scheduler": self.lr_scheduler,
                "monitor": self.params.lr_scheduler.monitor,
            },
        }

    def __init_optimizer(self):

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

    def __init_lr_scheduler(self):

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
