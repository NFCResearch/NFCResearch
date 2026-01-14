from joblib import dump, load
from mapie.classification import MapieClassifier
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import cross_val_score, train_test_split

num_cards = 52
score_thresh = 0.9
alpha = 0.2
one_high_len = 910
one_low_len = 3624
two_high_len = 900
two_low_len = 3599

data_sizes = [one_low_len, two_low_len, one_high_len, two_high_len, one_high_len + one_low_len,
             one_high_len + one_low_len + two_high_len, one_high_len + one_low_len + two_high_len + two_low_len]

print("Importing Models...")

model_names = [
            "OneLow",
            "TwoLow",
            "OneHigh",
            "TwoHigh",
            "TwoTypes",
            "ThreeTypes",
            "FourTypes",
        ]

one_high_len = 910
one_low_len = 3624
two_high_len = 900
two_low_len = 3599
models = []
for name in model_names:
    model = load("./Models/" + name + ".joblib")
    models.append(model)

print("Done Importing.")

print("Importing Responses...")
responses = []
response0 = np.load("./response0.npy", allow_pickle=True)
response1 = np.load("./response1.npy", allow_pickle=True)
response2 = np.load("./response2.npy", allow_pickle=True)
response3 = np.load("./response3.npy", allow_pickle=True)

responses.append(response0)
responses.append(response1)
responses.append(response2)
responses.append(response3)
responses.append(np.concatenate((responses[2], responses[0])))
responses.append(np.concatenate((responses[2],responses[0],responses[3])))
responses.append(np.concatenate(((responses[2],responses[0],responses[3],responses[1]))))

print("Done Importing Responses.")


print("Started Testing...")

tag_scores = np.zeros(num_cards)
tag_guess = None
data_size_used = 0
step_size_used = 0
for i in range(7):

    data_size_used += data_sizes[i]
    step_size_used += 1

    test_response = np.abs(responses[i]).reshape(1, -1)
    y_pred, y_psets = models[i].predict(test_response, alpha=alpha)
    tag_guesses = []
    for j in range(num_cards):
        val = y_psets[0][j]
        if val == True:
            tag_guesses.append(j)
    print(tag_guesses)
    # Update all tag scores
    for tag in tag_guesses:
        tag_scores[tag] = tag_scores[tag] + tag_guesses.count(tag)/len(tag_guesses)

    # Check if there is a only one max score
    is_unique_max = np.count_nonzero(tag_scores == max(tag_scores)) == 1
    if (is_unique_max and max(tag_scores) > score_thresh):
        tag_guess = np.argmax(tag_scores)
        break

print("Tag Guess: ",tag_guess)
print("Data Size Used: ", data_size_used)
print("Step Size Used: ", step_size_used)

