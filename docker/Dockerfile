
    FROM archlinux:latest
    RUN pacman -Syu --noconfirm
    RUN pacman -S python python-pip deno git --noconfirm
    RUN pip install numpy jax jaxlib torch torchvision ipdb regex validators setuptools wheel
    WORKDIR /app
    COPY ./__run__.py /app/run.py
    # CMD ["ls", "-lah", "/app"]
    COPY ./dev/yerbamate /app/yerbamate
RUN git clone https://github.com/ilex-paraguariensis/bombilla
RUN git clone https://github.com/ilex-paraguariensis/examples
COPY modified.json /app/modified.json
CMD ["python", "run.py"]
