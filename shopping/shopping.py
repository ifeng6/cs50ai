import csv
import sys

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

TEST_SIZE = 0.4
# each month's value corresponds to it's index in the array
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'June', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python shopping.py data")

    # Load data from spreadsheet and split into train and test sets
    evidence, labels = load_data(sys.argv[1])
    X_train, X_test, y_train, y_test = train_test_split(
        evidence, labels, test_size=TEST_SIZE
    )

    # Train model and make predictions
    model = train_model(X_train, y_train)
    predictions = model.predict(X_test)
    sensitivity, specificity = evaluate(y_test, predictions)

    # Print results
    print(f"Correct: {(y_test == predictions).sum()}")
    print(f"Incorrect: {(y_test != predictions).sum()}")
    print(f"True Positive Rate: {100 * sensitivity:.2f}%")
    print(f"True Negative Rate: {100 * specificity:.2f}%")


def load_data(filename):
    """
    Load shopping data from a CSV file `filename` and convert into a list of
    evidence lists and a list of labels. Return a tuple (evidence, labels).

    evidence should be a list of lists, where each list contains the
    following values, in order:
        - Administrative, an integer
        - Administrative_Duration, a floating point number
        - Informational, an integer
        - Informational_Duration, a floating point number
        - ProductRelated, an integer
        - ProductRelated_Duration, a floating point number
        - BounceRates, a floating point number
        - ExitRates, a floating point number
        - PageValues, a floating point number
        - SpecialDay, a floating point number
        - Month, an index from 0 (January) to 11 (December)
        - OperatingSystems, an integer
        - Browser, an integer
        - Region, an integer
        - TrafficType, an integer
        - VisitorType, an integer 0 (not returning) or 1 (returning)
        - Weekend, an integer 0 (if false) or 1 (if true)

    labels should be the corresponding list of labels, where each label
    is 1 if Revenue is true, and 0 otherwise.
    """
    evidence = []
    labels = []

    with open(filename, newline='') as csvfile:
        reader = csv.reader(csvfile)
        first = True
        for row in reader:
            # skip first row --> it's column headers
            if first:
                first = False
                continue
            data_point, label = process_row(row)
            evidence.append(data_point)
            labels.append(label)

    return (evidence, labels)


def process_row(row):
    data_point = []
    label = 0

    for i in range(len(row)):
        # int cases
        if i == 0 or i == 2 or i == 4 or i == 11 or i == 12 or i == 13 or i == 14:
            data_point.append(int(row[i]))
        # float cases
        elif i == 1 or i == 3 or i == 5 or i == 6 or i == 7 or i == 8 or i == 9:
            data_point.append(float(row[i]))
        # month case
        elif i == 10:
            data_point.append(months.index(row[i]))
        # trafficType
        elif i == 15:
            if row[i] == 'Returning_Visitor':
                data_point.append(1)
            else:
                data_point.append(0)
        # visitorType
        elif i == 16:
            if row[i] == 'TRUE':
                data_point.append(1)
            else:
                data_point.append(0)
        # label
        else:
            if row[i] == 'TRUE':
                label = 1

    return (data_point, label)


def train_model(evidence, labels):
    """
    Given a list of evidence lists and a list of labels, return a
    fitted k-nearest neighbor model (k=1) trained on the data.
    """
    model = KNeighborsClassifier(n_neighbors=1)
    model.fit(evidence, labels)
    return model


def evaluate(labels, predictions):
    """
    Given a list of actual labels and a list of predicted labels,
    return a tuple (sensitivity, specificity).

    Assume each label is either a 1 (positive) or 0 (negative).

    `sensitivity` should be a floating-point value from 0 to 1
    representing the "true positive rate": the proportion of
    actual positive labels that were accurately identified.

    `specificity` should be a floating-point value from 0 to 1
    representing the "true negative rate": the proportion of
    actual negative labels that were accurately identified.
    """
    num_positives = 0
    num_positives_correct = 0
    num_negatives = 0
    num_negatives_correct = 0

    for actual, prediction in zip(labels, predictions):
        # positive result
        if actual == 1:
            num_positives += 1
            # check if prediction is correct
            if prediction == 1:
                num_positives_correct += 1
        # negative result
        else:
            num_negatives += 1
            # check if prediction is correct
            if prediction == 0:
                num_negatives_correct += 1
    
    # calculate metrics
    sensitivity = num_positives_correct / num_positives
    specificity = num_negatives_correct / num_negatives

    return (sensitivity, specificity)


if __name__ == "__main__":
    main()
