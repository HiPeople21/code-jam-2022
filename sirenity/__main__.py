import uvicorn

import sirenity.app as sirenity


def main():
    """Starts the web server"""
    configuration = uvicorn.Config(
        sirenity.app,
    )
    server = uvicorn.Server(configuration)
    server.run()



if __name__ == "__main__":
    main()
