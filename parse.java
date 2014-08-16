
import java.io.*;
import java.util.*;

import sun.reflect.generics.tree.Tree;

import edu.stanford.nlp.dcoref.CorefChain;
import edu.stanford.nlp.dcoref.CorefCoreAnnotations.CorefChainAnnotation;
import edu.stanford.nlp.ling.CoreAnnotations.NamedEntityTagAnnotation;
import edu.stanford.nlp.ling.CoreAnnotations.PartOfSpeechAnnotation;
import edu.stanford.nlp.ling.CoreAnnotations.SentencesAnnotation;
import edu.stanford.nlp.ling.CoreAnnotations.TextAnnotation;
import edu.stanford.nlp.ling.CoreAnnotations.TokensAnnotation;
import edu.stanford.nlp.ling.CoreLabel;
import edu.stanford.nlp.pipeline.Annotation;
import edu.stanford.nlp.pipeline.StanfordCoreNLP;
import edu.stanford.nlp.semgraph.SemanticGraph;
import edu.stanford.nlp.semgraph.SemanticGraphCoreAnnotations.CollapsedCCProcessedDependenciesAnnotation;
import edu.stanford.nlp.trees.TreeCoreAnnotations.TreeAnnotation;
import edu.stanford.nlp.util.CoreMap;
import edu.stanford.nlp.*;



public class parse {
	
	public static void main(String arg[]) throws Exception
	{
		
		BufferedReader in = new BufferedReader(new FileReader(System.getProperty("user.dir")+"/input.txt")); 
		String text = in.readLine();
		String current;
		while((current = in.readLine()) != null){
			text = text+". "+current; 
		}
		in.close();
		
		PrintWriter out = new PrintWriter(new FileWriter(System.getProperty("user.dir")+"/output.txt")); 
		PrintWriter out1 = new PrintWriter(new FileWriter(System.getProperty("user.dir")+"/output1.txt")); 
		
		// creates a StanfordCoreNLP object, with POS tagging, lemmatization, NER, parsing, and coreference resolution 
	    Properties props = new Properties();
	    props.put("annotators", "tokenize, ssplit, parse");
	    StanfordCoreNLP pipeline = new StanfordCoreNLP(props);
	    
	    // read some text in the text variable
	    //String text = "the camera is amazing and easy to use. I love this ipod. the screen of the phone is the best";
	    
	    Annotation document = new Annotation(text);
	    pipeline.annotate(document);
	    
	    List<CoreMap> sentences = document.get(SentencesAnnotation.class);
	    
	    for(CoreMap sentence: sentences) {
	      SemanticGraph dependencies = sentence.get(CollapsedCCProcessedDependenciesAnnotation.class);
	      System.out.println(sentence);
	      System.out.println(dependencies.toList());
	      
	      out.println(sentence);
	      out.println(dependencies.toList());
	      out1.println(dependencies.toList());
	      
	      
	    }
	    out1.close();
	    out.close();
	    
	}
	
}
