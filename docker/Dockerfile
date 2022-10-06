FROM archlinux:latest
RUN pacman -Syu --noconfirm
RUN pacman -S python python-pip deno git --noconfirm
RUN pip install numpy jax torch torchvision ipdb regex validators setuptools wheel
WORKDIR /app
RUN git clone --recurse-submodules https://github.com/ilex-paraguariensis/yerbamate -b v2
WORKDIR /app/yerbamate
RUN mkdir dist
RUN python install.py
WORKDIR /app
RUN git clone https://github.com/ilex-paraguariensis/bombilla
WORKDIR /app/bombilla
RUN pip install -e .
WORKDIR /app
RUN git clone https://github.com/ilex-paraguariensis/examples
WORKDIR /app/examples
WORKDIR /app/examples/jax/mnist/mnist
COPY pull_and_run.py /app
WORKDIR /app
CMD ["python", "pull_and_run.py"]


