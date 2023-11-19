import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
import base64
from webapp.view_helpers import get_mongo, remove_substring_from_string

image_supplement = {
    'architecture': {'title': 'Model Architecture', 'caption': 'This diagram captures the overall architecture of the neural net model that you produced. The top row of the diagram represents the input layer, followed by hidden layers and the final output layer at the bottom. With each layer, there is a parentheses which provides important information regarding the shape of the model. The first number in the parentheses indicates the batch size used in the layer. Batch size refers to how many training examples are processed together in each training iteration.  In the input layer specifically, the second number in the parentheses indicate the shape or number of input features that the model expects. So if the input layer looks like this: (32, 8) that means there is a batch size of 32, and 8 input features which have been submitted to the layer. In the hidden layers and output layer, the second number in the parentheses indicates the number of neurons in each layer. For example, if a hidden layer has an input value of (32, 8) and an output value of (32, 64) this means that there are 64 neurons in this layer (and a batch size of 32). In each job default values are provided for the neural net model shape, however these values can be changed to your specifications (and those changes will be reflected in this diagram).'},
    'confusion_matrix': {'title': 'Confusion Matrix', 'caption': 'A confusion matrix is essential for evaluating the performance of the neural net model, and does so by providing a detailed breakdown of the model’s predictions and accuracy. The top left quadrant indicates the number of true negatives in the model. True negatives are instances where the model predicted a negative output and was correct (i.e. the model predicts no AD, and the individual actually doesn’t have AD). The bottom right box indicates the number of true positives, or cases where the model accurately predicts a positive output. In a classification model, high values in the top left and bottom right boxes are desired, because they indicate high accuracy of the model as a whole. Conversely, the top right box indicates the number of false positives: cases where the model predicted an output that was positive, when the real result was negative (i.e. the model predicts someone has AD when they actually do not). The bottom left box represents false negatives: cases where the model predicted that an output was negative when the result was actually positive. Low values in these boxes are desired, because they indicate relatively high accuracy and a low number of errors generated by the model. This visualization is useful to see if the classification model is relatively accurate and balanced, or if it skews heavily towards false positives or negatives. For example, if there are lots of false positives, and no false negatives, this could imply that the model is overly optimistic or aggressive in classifying instances as positive.'},
    'feature_importance': {'title': 'Feature Importance Diagram', 'caption': 'This feature importance diagram is relatively self explanatory, in the sense that it visualizes which features of the data had the most impact in the first layer of the model. It is important to note, after the first layer it becomes impossibly difficult to see which features have the most impact later on, so these weights may change over the course of the model. However, it can still provide some insight into which features and attributes of the data may have more impact on the prediction of AD. To see how input features such as function (FC) and location classification (LC) are determined, please reference the Classification Diagram on the home tab.'},
    'model_performance': {'title': 'Model Testing and Validation Performance', 'caption': 'There are two graphs here which provide further insight on the model performance. The left diagram displays the overall accuracy of the model during training and validation phases. Perfect accuracy, indicating the model always guesses accurately, is 1.0. On the right, the loss of the model is graphed as well. Loss is a fundamental metric which measures the differences between a model\'s predictions, and actual target values. In supervised learning, the goal is to minimize loss. Initially, the loss should be typically high because the model\'s weights are random, and its predictions are far from accurate. Looking at loss performance is essential because if the loss on the training data continues to decrease while the loss on a separate validation dataset starts increasing, it may indicate overfitting. Overfitting occurs when the model learns to fit the training data too closely and performs poorly on unseen data. On the other hand, if both the training and validation loss remain high or decrease too slowly, it may suggest underfitting, indicating that the model is too simple to capture the complexities of the data.'}
}

def get_all_jobs(request):
    email = request.user.email
    conn = get_mongo()
    doc = conn.AdNet.users.find_one({'id': email})
    return HttpResponse(json.dumps(doc['jobs']))


def get_ml_configurations(request):
    job_id = remove_substring_from_string(request.path, 'JobConfigurations/GetMLConfigurations/')[1:-1]
    return render(request, 'ml_configurations.html', {'content': job_id})


def get_results_view(request):
    job_id = remove_substring_from_string(request.path, 'JobConfigurations/Results/')[1:-1]
    return render(request, 'results_subpage.html', {'content': job_id})


def get_completed_jobs(request):
    conn = get_mongo()
    email = request.user.email
    doc = conn.AdNet.users.find_one({'id': email})
    jobs = doc['jobs']
    completed_jobs = []
    for job in jobs:
        if job['status'] == 'completed':
            completed_jobs.append(job)
    return HttpResponse(json.dumps(completed_jobs))


def create(request):
    info = request.GET.dict()
    conn = get_mongo()
    print("ok")
    user_doc = conn.AdNet.users.find_one({'id': request.user.email})
    new_config = {'name': info['name'], 'one': info['one'], 'two': info['two'],
                  'three': info['three'], 'four': info['four'], 'five': info['five'],
                  'ml_configs': {
                      'layers': [{'number': 1, 'size': 64, 'activation': 'relu'},
                                 {'number': 2, 'size': 64, 'activation': 'relu'}],
                      'final_activation': 'sigmoid',
                      'optimizer': 'adam',
                      'loss': 'binary_crossentropy',
                      'epochs': 10,
                      'batch_size': 32
                  },
                  'status': 'draft'}
    new_jobs = user_doc['jobs'] + [(new_config)]
    conn.AdNet.users.update_one({'id': request.user.email}, {"$set": {'jobs': new_jobs}})
    return HttpResponse({'success': True})


def edit(request):
    info = request.GET.dict()
    conn = get_mongo()
    user_doc = conn.AdNet.users.find_one({'id': request.user.email})
    new_config = {'name': info['name'], 'one': info['one'], 'two': info['two'],
                  'three': info['three'], 'four': info['four'], 'five': info['five'],
                  'status': info['status']}
    updated_jobs = []
    for job in user_doc['jobs']:
        if job['name'] != info['og_id']:
            updated_jobs.append(job)
        else:
            job['name'] = info['name']
            new_config['ml_configs'] = job['ml_configs']
    updated_jobs.append(new_config)
    conn.AdNet.users.update_one({'id': request.user.email}, {"$set": {'jobs': updated_jobs}})
    return HttpResponse({'success': True})


def check_if_possible(job, item):
    keys = ['one', 'two', 'three', 'four', 'five']
    full = True
    possible = True
    for k in keys:
        if job[k] == '':
            full = False
        if job[k] == item:
            possible = False
    if possible and not full:
        return True
    return False


def get_add_jobs(request):
    d = request.GET.dict()
    email = request.user.email
    conn = get_mongo()
    doc = conn.AdNet.users.find_one({'id': email})
    jobs = doc['jobs']
    edited_jobs = []
    for job in jobs:
        if job['status'] == 'draft':
            del job['ml_configs']
            del job['status']
            job['_id'] = job['name']
            del job['name']
            possible = check_if_possible(job, d['item'])
            if possible:
                edited_jobs.append(job)
    return HttpResponse(json.dumps(edited_jobs))


def get_results_data(request):
    job_id = remove_substring_from_string(request.path, '/JobConfigurations/GetResults/')
    user = request.user.email
    conn = get_mongo()
    results = conn.AdNet.Results.find_one({'user': user, 'job_id': job_id}, {'_id': 0})
    attrs = list(results.keys())
    attrs.pop(attrs.index('loss'))
    attrs.pop(attrs.index('acc'))
    attrs.pop(attrs.index('co'))
    attrs.pop(attrs.index('job_id'))
    if 'classification' in attrs:
        attrs.pop(attrs.index('classification'))
    attrs.pop(attrs.index('user'))
    image_list = []
    for image in attrs:
        image_info = {
            "filename": image,
            "content_type": 'image/png',
            "image_data": base64.b64encode(results[image]).decode('utf-8'),
            "title": image_supplement[image]['title'],
            "caption": image_supplement[image]['caption']
        }
        image_list.append(image_info)

    response_data = {"images": image_list}
    return JsonResponse(response_data)


def get_ml_for_job(request):
    job_id = remove_substring_from_string(request.path, '/JobConfigurations/GetMLForJob/')
    user = request.user.email
    conn = get_mongo()
    jobs = conn.AdNet.users.find_one({'id': user})['jobs']
    ml_configs = None
    for job in jobs:
        if job['name'] == job_id:
            if job['ml_configs'] == []:
                # prepopulate with default values
                job['ml_configs'] = {
                    'layers': [{'number': 1, 'size': 64, 'activation': 'relu'},
                               {'number': 2, 'size': 64, 'activation': 'relu'}],
                    'final_activation': 'sigmoid',
                    'optimizer': 'adam',
                    'loss': 'binary_crossentropy',
                    'epochs': 10,
                    'batch_size': 32
                }
                conn.AdNet.users.update_one({'id': request.user.email}, {"$set": {'jobs': jobs}})
            ml_configs = job['ml_configs']

    return HttpResponse(json.dumps(ml_configs))


def set_ml_configs(request):
    data = json.loads(request.body)
    conn = get_mongo()
    jobs = conn.AdNet.users.find_one({'id': request.user.email})['jobs']
    for layer in data['ml_configs']['layers']:
        if layer['size'] <= 0:
            return HttpResponse(json.dumps({'error': 'invalid_configuration'}))

    for job in jobs:
        if job['name'] == data['job_id']:
            job['ml_configs'] = data['ml_configs']
    conn.AdNet.users.update_one({'id': request.user.email}, {"$set": {'jobs': jobs}})
    return HttpResponse(json.dumps({'success': True}))


def add_item(request):
    keys = ['one', 'two', 'three', 'four', 'five']
    info = request.POST.dict()
    email = request.user.email
    conn = get_mongo()
    jobs = conn.AdNet.users.find_one({'id': email})['jobs']
    entered = False
    for job in jobs:
        if job['name'] == info['name']:
            for k in keys:
                if job[k] == '' and not entered:
                    job[k] = info['item']
                    entered = True
    if entered == False:
        return HttpResponse(json.dumps({'error'}))
    conn.AdNet.users.update_one({'id': request.user.email}, {"$set": {'jobs': jobs}})
    return HttpResponse(json.dumps({'success': True}))


def delete(request):
    info = request.GET.dict()
    conn = get_mongo()
    user_doc = conn.AdNet.users.find_one({'id': request.user.email})
    updated_jobs = []
    for job in user_doc['jobs']:
        if job['name'] != info['name']:
            updated_jobs.append(job)
    conn.AdNet.users.update_one({'id': request.user.email}, {"$set": {'jobs': updated_jobs}})
    conn.AdNet.Results.delete_one({'user': request.user.email, 'job_id': info['name']})
    return HttpResponse({'success': True})
