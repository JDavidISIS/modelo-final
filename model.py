from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from preprocessor import CustomPreprocessor

class MyModel:
    def __init__(self):
        self.model = make_pipeline(PolynomialFeatures(degree=2), LinearRegression())

    def train(self, X_train, y_train):
        self.model.fit(X_train, y_train)

    def predict(self, X):
        return self.model.predict(X)