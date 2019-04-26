package extras;

/**
 * Constants file which contains all the constant value being
 * used through the project
 * @author takkyon
 *
 */
public class Constants {

	private Constants() {
		
	}

	// index-terms
	public static final String TAG_CONTENTS = "contents";
	public static final String TAG_FILENAME = "filename";

	// folders
	public static final String CORPUS_FOLDER = "files/corpus";
	public static final String INDEX_FOLDER = "files/index";
	public static final String TASK_FOLDER = "files/task";
	public static final String QUERY_FILE = "files/query.txt";
	
	// other constants
	// public static final String[] queries = { "milky way galaxy", "hubble space telescope", "international space station", "big bang theory", "mars exploratory missions" };
	public static String[] queries = null;
	public static String[] queryFileNames = null;
	public static final int N[] = { 4, 6, 8, 10 };
	public static final int K[] = { 10, 20 };
	public static final int topFreqTermsToRemove = 50;
}
