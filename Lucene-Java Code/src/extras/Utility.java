package extras;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;

import org.apache.lucene.document.Document;
import org.apache.lucene.search.IndexSearcher;
import org.apache.lucene.search.ScoreDoc;
import org.apache.lucene.search.TopDocs;

/**
 * Utility class which has all the functions
 * used throughout the project files
 * @author takkyon
 *
 */
public class Utility {

	/**
	 * Initialization steps:
	 * 	> Delete all the files from the index folder
	 * @throws IOException
	 */
	public void init() throws IOException {
		File file = new File(Constants.INDEX_FOLDER);
		if(file.exists()) {
			for(File f: file.listFiles())
				f.delete();
		}
	}
	
	/**
	 * Get document title from the top documents
	 * @param topDocs
	 * @param searcher
	 * @return
	 * @throws IOException
	 */
	public List<String> getDocumentTitle(TopDocs topDocs, IndexSearcher searcher) throws IOException {
		List<String> documents = new ArrayList<>();
		for(ScoreDoc scoreDoc: topDocs.scoreDocs) {
			Document document = searcher.doc(scoreDoc.doc);
			documents.add(document.get(Constants.TAG_FILENAME) + "  " + scoreDoc.score);
		}
		return documents;
	}
	
	/**
	 * Sort hashmap by value (descending order)
	 * @param hm
	 * @return
	 */
	public Map<String, Double> sortByValue(Map<String, Double> hm) 
    { 
        // Create a list from elements of HashMap 
        List<Map.Entry<String, Double> > list = 
               new LinkedList<Map.Entry<String, Double> >(hm.entrySet()); 
  
        // Sort the list 
        Collections.sort(list, new Comparator<Map.Entry<String, Double> >() { 
            public int compare(Map.Entry<String, Double> o1,  
                               Map.Entry<String, Double> o2) 
            { 
            		return o2.getValue().compareTo(o1.getValue());
            } 
        }); 
          
        // put data from sorted list to hashmap  
        Map<String, Double> temp = new LinkedHashMap<String, Double>(); 
        for (Map.Entry<String, Double> aa : list) { 
            temp.put(aa.getKey(), aa.getValue()); 
        } 
        return temp; 
    } 
	
}
