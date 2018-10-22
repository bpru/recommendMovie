from flask import *
from utils import *
import pandas as pd
app = Flask(__name__)

@app.route("/")
def index():
    df = pd.read_csv('../data/processed.csv')
    selected_title = 'Toy Story'
    table = get_recommendation_by_title(df, selected_title)[['title', 'year', 'weighted_rating']]
    print(table.to_html())
    return render_template('view.html', table=table.to_html(), watched=selected_title)

if __name__ == "__main__":
    app.run(debug=True)