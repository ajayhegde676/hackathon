from flask import Flask, jsonify, request
import json
import pandas as pd

app = Flask(__name__)


@app.route('/', methods=['GET'])
def home():
    return "WELCOME"


@app.route('/prediction', methods=['POST'])
def prediction():
    data = request.json
    area = data['area']
    crop = data['crop'].lower()
    district = data['district'].lower()
    market_price = 0
    bengal_gram, ground_nut, maize = 0, 0, 0
    adilabad, bhadradri, hyderabad, jagtial = 0, 0, 0, 0
    graph_data = []
    if crop.lower() == 'bengal_gram':
        bengal_gram = 1
        market_price = 52.3
    elif crop.lower() == 'ground_nut':
        ground_nut = 1
        market_price = 51.48
    elif crop.lower() == 'maize':
        market_price = 21
        maize = 1
    else:
        return jsonify({"status": 400,
                        })
    if district.lower() == 'adilabad':
        adilabad = 1
    elif district.lower() == 'bhadradri':
        bhadradri = 1
    elif district.lower() == 'hyderabad':
        hyderabad = 1
    elif district.lower() == 'jagtial':
        jagtial = 1

    try:
        df = pd.read_csv('4_dist.csv')
        X = df[["district_adilabad", "district_bhadradri", "district_hyderabad", "district_jagtial", "crop_bengal_gram",
                "crop_groundnut", "crop_maize", "Acre"]]
        Y = df["Total_Yield"]
        from sklearn import linear_model
        regr = linear_model.LinearRegression()
        regr.fit(X, Y)
        prediction = regr.predict([[adilabad, bhadradri, hyderabad, jagtial, bengal_gram, ground_nut, maize, area]])
        index_list = df.index[(df['district_'+district]==1)&(df['crop_'+crop]==1)].tolist()
        for index in index_list:
            sub_response = {}
            sub_response['year'] = int(df['Year'][index])
            sub_response['min_temp'] = df['Min_Temp'][index]
            sub_response['max_temp'] = df['Max_Temp'][index]
            sub_response['rainfall'] = df['Total_Rainfall'][index]
            graph_data.append(sub_response)
    except Exception as e:
        print(e)
        return jsonify({"status": 400,
                        "message": "model"
                        })

    return jsonify({
        'status': 200,
        'prediction': round(prediction[0]),
        'profit':  round(prediction[0] * market_price),
        'graph_data': graph_data
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
