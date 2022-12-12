import Server from "./server"


console.log(process.argv)
new Server(process.argv.at(-1)!);
