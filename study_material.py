from serpapi import GoogleSearch

def scholar_section(query):
    if not query:
        return "No query provided."
    
    params = {
        "engine": "google_scholar",
        "q": query,
        "api_key": "f9e0477cf0dc8577e05f6abd7955c2dcfde1dbea87def92f9d5cb2206d2b5983"
    }

    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        organic_results = results.get("organic_results", [])
        
    except Exception as e:
        print(f"Error fetching results: {e}")
        return []
    formatted_results = []
    for result in organic_results:
        title = result.get('title', 'No title')
        link = result.get('link', 'No link')
        snippet = result.get('snippet', 'No snippet')
        
        formatted_result = f"Title: {title}\n\nLink:\n {link}\n\nSnippet:\n{snippet}"
        formatted_results.append(formatted_result)
    
    return formatted_results

