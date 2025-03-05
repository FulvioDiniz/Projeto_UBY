from flask import Flask, request, jsonify
from pycomm3 import LogixDriver
plc_ip = '192.168.0.10'

app = Flask(__name__)

def set_peso(plc_ip, peso):
    with LogixDriver(plc_ip) as plc:
        plc.write('PESO', peso)
        print("Peso enviado para o CLP.")

@app.route('/setpeso', methods=['POST'])
def setpeso_endpoint():
    plc_ip = request.form.get('plc_ip')
    peso = request.form.get('peso')
    if plc_ip is None or peso is None:
        return jsonify({'status': 'Erro: parâmetros ausentes.'}), 400

    # Converter peso para o tipo desejado, se necessário (por exemplo, float ou int)
    try:
        peso = float(peso)
    except ValueError:
        return jsonify({'status': 'Erro: peso inválido.'}), 400

    set_peso(plc_ip, peso)
    return jsonify({'status': 'Peso enviado para o CLP.'})

if __name__ == '__main__':
    app.run(debug=True)
