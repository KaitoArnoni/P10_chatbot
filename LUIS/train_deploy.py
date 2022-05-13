import os, json, time
from dotenv import load_dotenv, find_dotenv
from azure.cognitiveservices.language.luis.authoring import LUISAuthoringClient
from azure.cognitiveservices.language.luis.runtime import LUISRuntimeClient
from msrest.authentication import CognitiveServicesCredentials

load_dotenv()

# chargement des variables
authoring_key = os.getenv('AUTHORING_KEY')
authoring_endpoint = os.getenv('AUTHORING_ENDPOINT')
client = LUISAuthoringClient(authoring_endpoint, CognitiveServicesCredentials(authoring_key))



prediction_key = os.getenv('AUTHORING_KEY')
predictionEndpoint = os.getenv('PREDICTIONENDPOINT')
luisSlotName = 'production'
runtimeCredentials = CognitiveServicesCredentials(prediction_key)
clientRuntime = LUISRuntimeClient(endpoint=prediction_endpoint, credentials=runtimeCredentials)


# création client / runtime
# Instantiate clients
def instantiate_client():
    # LUIS Authoring client
    client = LUISAuthoringClient(
        authoring_endpoint,
        CognitiveServicesCredentials(authoring_key))
    
    # LUIS Runtime Client
    clientRuntime = LUISRuntimeClient(
        predictionEndpoint,
        CognitiveServicesCredentials(predictionKey))
    
    return client, clientRuntime

print('Instantiate client(s)...')
client, clientRuntime = instantiate_client()
print()

# chargement des jeux de données
# jeu d'entrainement

JSON_PATH_LUIS = "/Users/kaju/Documents/FORMACAO IA OPENCLASSROOMS/PROJET 10 - DEVELOPPEZ UN CHATBOT POUR RESERVER DES VACANCES/P10_ARNONI_KAITO/ARNONI_KAITO_2_LUIS_042022/"


file_path = os.path.join(JSON_PATH_LUIS, "utterances_train.json")
with open(file_path, "r") as f:
    utterances_train = json.load(f)

file_path = os.path.join(JSON_PATH_LUIS, "utterances_test.json")
with open(file_path, "r") as f:
    utterances_test = json.load(f)


# Création application
def create_app():
# Create a new LUIS app
    app_name = "LuisP10_app {}".format(datetime.datetime.now())
    app_desc = "Projet_10_MVP_Flight_booking"
    app_version = "1"
    app_locale = "en-us"

    app_id = client.apps.add(dict(name=app_name,
                                  initial_version_id=app_version,
                                  description=app_desc,
                                  culture=app_locale))

    print("LUIS app {}\n crée with ID {}".format(app_name, app_id))
    return app_id, app_version

print("Creating application...")
app_id, app_version = create_app()
print()

# création intents
def add_intents(app_id, app_version):
    intentId = client.model.add_intent(app_id, app_version, "book_flight")

    print("Intention book_flight {} ajouté.".format(intentId))

print ("Ajout d'intention à l'application...")
add_intents(app_id, app_version)
print ()

# création entities
# addEntities
def add_entities(app_id, app_version):
    from_cityEntityId = client.model.add_entity(app_id, app_version, name="from_city")
    print("from_cityEntityId {} entité crée.".format(from_cityEntityId))
    
    to_cityEntityId = client.model.add_entity(app_id, app_version, name="to_city")
    print("to_cityEntityId {} entité crée.".format(to_cityEntityId))
    
    from_dtEntityId = client.model.add_entity(app_id, app_version, name="from_dt")
    print("from_dtEntityId {} entité crée.".format(from_dtEntityId))
    
    to_dtEntityId = client.model.add_entity(app_id, app_version, name="to_dt")
    print("to_dtEntityId {} entité crée.".format(to_dtEntityId))
    
    budgetEntityId = client.model.add_entity(app_id, app_version, name="budget")
    print("budgetEntityId {} entité crée.".format(budgetEntityId))

print ("Ajout d'entités à l'application...")
add_entities(app_id, app_version)
print ("Opération terminée.")

def create_utterance(intent, utterance, *labels):

    text = utterance.lower()

    def label(name, value):
        value = value.lower()
        start = text.index(value)
        return dict(entity_name=name, start_char_index=start,
                    end_char_index=start + len(value))

    return dict(text=text, intent_name=intent,
                entity_labels=[label(n, v) for (n, v) in labels])

def add_utterances(app_id, app_version):
    # Now define the utterances
    utterances = [create_utterance("book_flight", "book flight from London to Paris on May 22, 2021 returning june 21, 2021 for $200",
                                ("from_city", "London"),
                                ("to_city", "Paris"),
                                ("from_dt", "May 22, 2021"),
                                ("to_dt", "june 21, 2021"),
                                ("budget", "$200"))]

    # Add the utterances in batch. You may add any number of example utterances
    # for any number of intents in one call.
    client.examples.batch(app_id, app_version, utterances)
    print("{} Exemple d’énoncé ajouté.".format(len(utterances)))

print ("Ajout d'exemple à l'application...")
add_utterances(app_id, app_version)
print ()


# entraînement
def train_app(app_id, app_version):
    response = client.train.train_version(app_id, app_version)
    waiting = True
    while waiting:
        info = client.train.get_status(app_id, app_version)

        # get_status returns a list of training statuses, one for each model. Loop through them and make sure all are done.
        waiting = any(map(lambda x: 'Queued' == x.details.status or 'InProgress' == x.details.status, info))
        if waiting:
            print ("Attendez 10 secondes pour que l'apprentissage se termine...")
            time.sleep(10)

print ("Apprentissage de l’application ...")
train_app(app_id, app_version)
print ()


def get_params(endpoint, app_version, prediction_key, app_id):
    """Renvoie les paramètres de l'app LUIS"""
    
    # On envoie la requête permettant d'exporter le modèle au format json
    response = requests.get(
        url=f"{endpoint}luis/authoring/v3.0-preview/apps/{app_id}/versions/{app_version}/export",
        params={
            "format": "json"
        },
        headers={
            "Ocp-Apim-Subscription-Key": prediction_key,
        }
    )
    
    # On vérifie la réponse
    check_response_ok_or_raise_for_status(response)
    
    # On renvoie les paramètres
    return response.json()

param = get_params(authoring_endpoint,"1",authoring_key, app_id)

file_path = os.path.join(JSON_PATH_LUIS, "param.json")
with open(file_path, "w") as f:
    json.dump(param, f)

# publication app
def publish_app(app_id, app_version):
    client.apps.update_settings(app_id, is_public=True)
    responseEndpointInfo = client.apps.publish(app_id, app_version, is_staging=False)
    print("Point de terminaison: " + responseEndpointInfo.endpoint_url)

print ("On publie l'application...")
publish_app(app_id, app_version)


# prediction
def predict(app_id, slot_name):

    request = { "query" : ["book flight from London to Paris on May 22, 2021 returning june 21, 2021 for $300"]}

    # Note be sure to specify, using the slot_name parameter, whether your application is in staging or production.
    response = clientRuntime.prediction.get_slot_prediction(app_id=app_id, slot_name=slot_name, prediction_request=request)

    print("Top intent: {}".format(response.prediction.top_intent))
    #print("Sentiment: {}".format (response.prediction.sentiment))
    print("Intents: ")

    for intent in response.prediction.intents:
        print("\t{}".format (json.dumps (intent)))
    print("Entities: {}".format (response.prediction.entities))
    return response.as_dict()

print ("Prédiction:")
pred = predict(app_id, "Production")


# Supprimer la version 
def delete(endpoint, app_version, app_key, app_id):
    
    # On crée le client avec les informations d'authentification
    client = LUISAuthoringClient(endpoint, prediction_key)

    # On delete la version de l'app
    client.versions.delete(app_id, app_version)

delete(authoring_endpoint,"1",authoring_key, app_id)


# Créer une nouvelle version
def new_version(authoring_endpoint, app_id, authoring_key, app_version, app_params: dict, app_utterances: list=[]):
    """Crée un nouvelle version de l'application"""
    
    # On ajoute les utterances aux paramètres de l'application
    app_params_tmp = app_params.copy()
    app_params_tmp["utterances"] += app_utterances
    
    # On envoie la requête permettant de créer la nouvelle version
    response = requests.post(
        url=f"{authoring_endpoint}luis/authoring/v3.0-preview/apps/{app_id}/versions/import",
        params={
            "versionId": app_version,
        },
        headers={
            "Ocp-Apim-Subscription-Key": authoring_key,
        },
        json=app_params_tmp
    )
    
    # On vérifie la réponse
    check_response_ok_or_raise_for_status(response)


file_path = os.path.join(JSON_PATH_LUIS, "param.json")
with open(file_path, "r") as f:
    app_params = json.load(f)


app_version = "final"
new_version(authoring_endpoint, app_id, authoring_key, app_version, app_params, utterances_train)

print ("Apprentissage de l’application ...")
train_app(app_id, app_version)
print ()

param = get_params(authoring_endpoint,app_version,authoring_key, app_id)

file_path = os.path.join(JSON_PATH_LUIS, "param.json")
with open(file_path, "w") as f:
    json.dump(param, f)


#Publier l'application dans l’emplacement de production
print ("On publie l'application...")
publish_app(app_id, app_version)

#Evaluation du nouveau modèle
    
def check_response_ok_or_raise_for_status(response):
    """Vérifie que la réponse est ok ou génère une erreur"""
    
    # On génère une exception en cas d'erreur
    if not response.ok:
        print(response.content)
        response.raise_for_status()

def evaluate(endpoint, app_id, prediction_key, utterances: list, check_status_period: int=10):
    """Evaluation de l'application LUIS sur un jeu de test"""
    
    # On envoie la requête permettant de lancer l'évaluation
    response = requests.post(
        url=f"{endpoint}luis/v3.0-preview/apps/{app_id}/slots/production/evaluations",
        headers={
            "Ocp-Apim-Subscription-Key": prediction_key,
        },
        json=utterances
    )
    
    # On vérifie la réponse
    check_response_ok_or_raise_for_status(response)
    
    # On récupère l'id de l'opération
    operation_id = response.json()["operationId"]
    
    waiting = True
    while waiting:
        # On check le status
        response = requests.get(
            url=f"{endpoint}luis/v3.0-preview/apps/{app_id}/slots/production/evaluations/{operation_id}/status",
            headers={
                "Ocp-Apim-Subscription-Key": prediction_key,
            }
        )
        
        # On vérifie s'il y a une erreur
        if response.json()["status"] == "failed":
            raise ValueError(response.content)
        
        waiting = response.json()["status"] in ["notstarted", "running"]
        
        if waiting:
            time.sleep(check_status_period)
        
    # On récupère les résultats de l'évaluation
    response = requests.get(
        url=f"{endpoint}luis/v3.0-preview/apps/{app_id}/slots/production/evaluations/{operation_id}/result",
        headers={
            "Ocp-Apim-Subscription-Key": prediction_key,
        }
    )
    
    # On récupère les résultats
    res = response.json()
    
    # On met en forme les résultats dans un DataFrame
    res = pd.DataFrame(res["intentModelsStats"] + res["entityModelsStats"])
    res.iloc[:, -3:] = res.iloc[:, -3:].astype(float)
    res.columns = [
        "model_name",
        "model_type",
        f"precision",
        f"recall",
        f"f_score",
    ]
    
    return res


results = evaluate(prediction_endpoint, app_id, prediction_key, utterances_test)
