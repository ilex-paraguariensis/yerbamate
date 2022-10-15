import os
def run():
    cwd = os.getcwd()
    os.chdir(os.path.dirname(__file__))
    os.system(f"deno run --allow-net --allow-read --allow-env --allow-run --unstable server.ts {cwd}")
    
