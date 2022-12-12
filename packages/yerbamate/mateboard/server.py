import os


def run():
    cwd = os.getcwd()
    os.chdir(os.path.join(os.path.dirname(__file__), "server"))
    # os.system(f"deno run --allow-net --allow-read --allow-env --allow-run --unstable server.ts {cwd}")
    os.system(f"npm run start:dev {cwd}")
