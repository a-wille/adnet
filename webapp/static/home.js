function getCookie(name) {
    //returns cookie
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

$(document).ready(function () {

    const backgroundTemplate = '<div id="container"><h4 class="k-h4">Alzheimer’s Disease</h4><img id="dna_snp" src="/home/acretan/capstone/webapp/static/img/dna_snp.png" alt="SNP Diagram" /><p class="k-paragraph">Alzheimer’s disease (AD) is an illness that affects just under 6 million Americans presently, and this number is expected to only increase as time goes on. Since AD can start developing in individuals almost 20 years before symptoms actually become visible, models that can help predict an individual’s susceptibility to the disease early on are crucial. Early detection and prediction of AD allows for preventative action and medication before harmful components (e.g.  tangles and plaques) have a chance to build up in the brain. A significant amount of research has already been conducted studying the effect of a single gene on the prevalence of Alzheimer’s disease. Unfortunately, there is no singular gene that has been found to directly cause AD. While certain genetic markers and mutations may increase risk, these individual events do not determine conclusively whether an individual will develop the disease.</p><br><p class="k-paragraph"> Mutations on a single gene are only one of many ways in which diseases can be caused in the human body. Because genes interact in countless ways, many diseases can be caused by mutations in multiple genes (also known as multifactorial disorders). Alzheimer’s disease is an example of a multi-factorial disorder, however there is no combination of genetic mutations that is known to successfully predict AD thus far. The goal of this project is to allow individuals to compare the effect of different combinations of genetic mutations as they relate to the prediction of Alzheimer’s disease. </p></div><br><br>' +
        '<div id="container"><h4 class="k-h4">SNP Significance</h4><p class="k-paragraph"><img class="k-image" id="snp_amino" src="/home/acretan/capstone/webapp/static/img/snp_consequence.jpg" alt="Amino Acid SNP Effect" />This project focuses on single nucleotide polymorphisms (SNPs) which are single point genetic mutations that exist within one’s genome. SNPs are known to have anywhere from negligible to severe effects within one’s cells. One SNP in a protein-coding gene might change a base pair in such a way that the resulting amino acid stays the same. Another might change an intermediate codon into a stop codon, which terminates protein coding abruptly and severely damages the resulting structure and function. In other cases, SNPs are used as genetic markers which can help identify genetic disorders, as well as hint at an individual\'s susceptibility to certain drugs or toxins. Because SNPs can indicate an increased or decreased susceptibility to an illness (and because SNPs are quite common within genes), they can be used together to help predict the likelihood of someone becoming symptomatic of an illness such as AD.</p></div><br><br>' +
        '<div id="container"><h4 class="k-h4">What is a neural net model?</h4><img class="k-image" id="neural_net" src="/home/acretan/capstone/webapp/static/img/neural_net_layout.png" alt="Neural Net" /><p class="k-paragraph">A neural network model is like a simplified artificial representation of the human brain\'s decision-making process. Just as our brains consist of interconnected neurons that process and transmit information, a neural network comprises artificial neurons or \'nodes\' organized into layers. Each node takes in information, processes it, and passes it to the next layer. These nodes work together to recognize patterns and make predictions based on data. By training a neural network on genetic data, we can teach it to recognize complex genetic patterns and make predictions about genetic outcomes, such as disease risk or trait inheritance.</p><br><p class="k-paragraph">Much like how our brain learns from experience, a neural network \'learns\' from large datasets, adjusting the \'weights\' of its connections to improve its ability to make accurate predictions. Neural networks can be configured in several daifferent ways to influence its performance. Activation functions, such as ReLU or Sigmoid, determine how neurons in each layer respond to inputs, impacting the model\'s ability to capture complex patterns. Optimization algorithms, such as Adam or SGD, control how the model learns by adjusting weights during training, with learning rates affecting the size of weight updates. Furthermore, the neural network can have various numbers of layers (neurons in each level), allowing you to create models of varying complexity to match the problem\'s intricacy. Loss functions are chosen to align the network\'s objectives, defining the measure of error used for training. Finally, batch size and the number of training epochs affect the training process\'s efficiency and generalization capability. Adjusting these components carefully can significantly impact a neural network\'s accuracy, speed of convergence, and suitability for specific tasks. For further details on terms such as activation function, loss function, etc. please reference the glossary section of this application!</p><br><p class="k-paragraph">Each job that you create in this application is equivalent to one neural net model. It is worth noting that the number of input features for any model in this application are automatically generated and are equal to 4N, where N represents the number of SNPs selected for a job. Beyond the input and the output layer however, all hidden layers can be configured by the user to their specifications.</p></div>'

    const useTemplate = '<div id="container"><h4 class="k-h4">Overview</h4><p class="k-paragraph">As mentioned earlier, this web tool focuses on allowing users to build predictive models for AD. This works by having users select up to 5 SNPs, and submitting them as a ‘job’. On the back-end, the job will take those SNPs and use them as input arguments for a neural network model whose goal is to predict the likelihood of developing AD. Once the job is complete, results will be returned and the user will be able to see how well those SNPs worked at predicting AD diagnoses. This allows users to investigate multiple SNP interactions to find potential markers and indicators of the illness.</p></div>' +
                        '<br><div id="container"><h5 class="k-h5">Unverified Users</h5><p class="k-paragraph">In order to create and submit jobs, a user must register with a .edu email and wait for account verification. Account verification may take up to a week to be processed, however once verified the user will be notified via email as to their account status. Unverified users are still able to research various genes and SNPs, but they are unable to submit and create jobs until their account is approved and verified by an administrator.</p><br>' +
                            '<h5 class="k-h5">Verified Users</h5><p class="k-paragraph">Verified users are able to research various genes and SNPs on this application before adding specific SNPs to various jobs of their choosing. Once SNPs have been selected (up to five values), then the user may choose to customize their job further by specifying the configuration of their machine learning settings. Examples of various configurations include adding layers, increasing neuron size in already existing layers, changing the activation function, etc. If the user does not wish to change these settings, default values have already been preloaded. These preloaded values can be seen anytime a new job is created in the ML Settings button.</p>' +
        '<p class="k-paragraph">When a job is ready to be submitted, the user can send the job for training and testing. Due to the computationally intensive nature of training and validating a neural net model, a user may only process one job at a time. However, if a user wishes to submit multiple jobs at once, they are able to do so, with all additional jobs being placed in a queue. Once the first job in the queue is complete, the next one will be sent until the queue is empty. This way, users don’t have to sit and wait for results before sending another job. Once a job is completed, an email will be sent to a user to notify them. Users can see how well the model ran by clicking the Results button for the job in the Results tab. Different visualizations of the model performance are provided and explained in this section as well. Users may then use the feedback from how a neural net model ran to try and improve with either new SNP combinations, or different neural net model configurations.</p></div>';

    const classTemplate = '<div id="container"><h4 class="k-h4">Classification of SNPs</h4></div><p class="k-paragraph">SNPs have four attributes that are used as input features for the neural net model: functional class, location class, risk, and chromosome. Functional class, risk level, and location class are all based on Ensembl’s annotation for the SNPs. For the definition of each functional class and its consequences, please reference the glossary. All variant class definitions and their respective locations can be seen in the image below, the location class being based on the general region of the gene where an SNP takes place. The risk value for each SNP also comes from the respective Ensembl annotation (and is shown for each SNP in our grid). The risk level for an SNP ranges from MODIFIER (meaning the effect is negligible) to HIGH (which implies severe protein damage). For further details on Ensembl annotations and definitions, please reference the Glossary or the <a href="https://useast.ensembl.org/info/genome/variation/prediction/predicted_data.html">Ensembl documentation.</a> </p><img id="classification" src="/home/acretan/capstone/webapp/static/img/classification_diagram.png" alt="Classification Diagram" />';

    const interpretTemplate = '<p>This is some relevant text for Item 2.</p><img src="/home/acretan/capstone/webapp/static/img/neural_net_diagram.png" alt="Image 2" />';


    $("#panelbar").kendoPanelBar({
        expandMode: "multiple", // Set your preferred expand mode
        dataSource: [
            {
                text: "Background",
                content: backgroundTemplate // Set the template for Item 1
            },
            {
                text: "How To Use",
                content: useTemplate // Set the template for Item 2
            },
            {
                text: "Classification of SNPs",
                content: classTemplate// Set the template for Item 2
            },
            {
                text: "Interpreting Results",
                content: interpretTemplate // Set the template for Item 2
            }
            // Add more items with templates as needed
        ]
    });


});
