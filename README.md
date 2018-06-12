## LIN205B
Calculating syntactic complexity of a sentence. 

### How to run

1. Install StanfordCoreNLP and run the server on your local machine using the following command :
```
java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port 9000 
-timeout 15000
```
2. Clone the repository and replace the filepath as required in the code. 
3. Run the code by : 

```
python calculate_scores.py
```
