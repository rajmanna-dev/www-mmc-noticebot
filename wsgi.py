from waitress import serve
import app

if __name__ == '__main__':
    serve(app.app, host='192.168.0.101', port=8080)