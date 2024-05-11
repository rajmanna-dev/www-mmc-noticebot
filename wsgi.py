from waitress import serve
import main

if __name__ == '__main__':
    serve(main.app, port=int("3000"))