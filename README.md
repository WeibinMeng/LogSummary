# LogSummary

### Requirements

Requirements are listed in `requirements.txt`. 

​	gensim=3.8.1 numpy=1.17.2 networkx=2.4 rouge=1.0.0

To install these, run:

```
pip install -r requirements.txt
```



#### OpenIE Methods Installation

For most methods, it requires to have Java installed additionally to Python as it runs third party tools.

##### Stanford

Install the Stanford CoreNLP from [here](https://stanfordnlp.github.io/CoreNLP/index.html#download). Then update the `openie.ini` config file within the `openie ` package.

##### Ollie

Install Ollie using their "Local Machine" installation process you can find [here](https://github.com/knowitall/ollie#local-machine). Then update the `openie.ini` config file within the `openie` package.

##### OpenIE5

Install OpenIE5 using their pre-compiled stand-alone JAR you can find [here](https://github.com/dair-iitd/OpenIE-standalone#using-pre-compiled-openie-standalone-jar).

Before using OpenIE5 you will need to run it as a server using a command similar to this one: ``java -Xmx10g -XX:+UseConcMarkSweepGC -jar openie-assembly-5.0-SNAPSHOT.jar --httpPort 8000 `` executing the downloaded stand-alone JAR. This is explained [here](https://github.com/dair-iitd/OpenIE-standalone#running-as-http-server) in their repo.

Additionally, it requires a python wrapper you can find [here](https://github.com/vaibhavad/python-wrapper-OpenIE5) which is already installed when you install the ``requirements.txt``.

##### PredPatt

Proceed to install PredPatt as they explain it in their repo [here](https://github.com/hltcoe/PredPatt/blob/master/doc/get-started.md#installation). 

##### ClausIE

Download ClauseIE from their source [here](https://www.mpi-inf.mpg.de/departments/databases-and-information-systems/software/clausie/). Update the `openie.ini` file using its directory for the jar location.

##### PropS

Clone [this repo]() where PropS has been upgraded to Python 3.8. Then you will need to update the config file at `openie.ini` and specify its package directory. 



#### Configuration File

After installing the OpenIE methods above, make sure to update the `openie.ini` configuration file located inside the `openie` package according to your installation. It provides part of the settings for running the OpenIE methods that depend on Java such as StanfordNLP or external Python packages such as PropS.



### Quick Start

#### Input Format

##### Templates

```json
{
    "<id1>": [
        "< online template >",
        "< ground truth template >",
        [
            [
                "arg1",
                "predicate",
                "arg2"
            ],
            [< more triples >],
            [< more triples >]
        ]
    ],
    "<id2>":[...]
 }
```



##### Raw logs

Although logs have more freedom in their format as their preprocessing details are specific to each log type, the current expected format of  most logs is the following. 

```
<log_idx1>\t<log_message1>
<log_idx2>\t<log_message2>
...
```

Only the original switch logs format is expected to not have and index and be simply the log message.

```
<log_message1>
<log_message2>
...
```



#### Run LogIE

After the installation, run the following command in the home directory where this project is located.

```bash
python -m LogIE.run --templates "<Templates File>" --evaluation lexical --rules new --openie predpatt
```

#### Arguments

```
Runs information extraction from logs.

arguments:
  -h, --help            show this help message and exit
  --templates templates
                        input raw templates file path (default: None)
  --raw_logs raw_logs   input raw raw_logs file path (default: None)
  --base_dir base_dir   base output directory for output files (default: ['<Project Folder>\\output'])
  --log_type log_type   Input type of templates. (default: ['original'])
  --rules rules         Predefined rules to extract triples from templates. (default: None)
  --evaluation evaluation [evaluation ...]
                        Triples extraction evaluation metrics. (default: [])
  --openie openie       OpenIE approach to be used for triple extraction. (default: ['stanford'])
  --id id               Experiment id. Automatically generated if not specified. (default: None)
  --tag                 Tag variables in the output triples (i.e. [([variable])] ). (default: False)
  --save_output         Save the output of logs or templates triples. (default: False)
  --force               Force overwriting previous output with same id. (default: False
```



#### Examples

#### Only generate output from LogIE

This command only generates output from LogIE without evaluation using the provided online templates in their corresponding field of the json format specified above. The ground truth will be disregarded to generate this output. 

```bash
python -m LogIE.run --templates "<Templates File Path>" --"<Raw Logs File Path>" --rules new --openie <OpenIE approach> --save_output --tag
```

Please note that `--tag` will tag the variables in the output triples (i.e. [([variable])] ).

#### Rank Summaries

```bash
python summarization.py --type Proxifier --model model/Proxifier.model --evaluate 1 --topk 5 #evaluation mode
```


