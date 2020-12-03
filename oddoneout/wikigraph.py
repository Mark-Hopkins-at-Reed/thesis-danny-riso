"""
wikigraph.py

Implements the WCGTaxonomy subclass of the Taxonomy class.

It is intended to access the structure of the Wikipedia Category Graph,
derived from the enwiki categorylinks and pages files,
so it can be ordered into an ontology.
"""

import copy
from taxonomy import Taxonomy, Specificity
from wiki_demo import findPagesInCategory, findPagesById


class WCGTaxonomy(Taxonomy):
    
    def __init__(self, categorylinks_filename, pages_filename):
        self.specificity = Specificity()
        self.catlinks = getAllCategories(categorylinks_filename)
        self.pages = getAllPages(pages_filename)
        self.num_insts = len(self.get_descendant_instances(self.get_root()))
        
    def is_instance(self, node):
        return node in self.pages and self.specificity(self, node) == 0
    
    def is_category(self, node):
        return node in self.catlinks and self.specificity(self, node) > 0
    
    def num_instances(self):
        return self.num_insts
    
    def get_root(self):
        # For now, use "'Recipes'" as a guaranteed root with many subcategories.
        # When looking at the entire enwikibooks, use "'Categories'"
        return "'Recipes'"
    
    def get_ancestor_categories(self, node):
        # Given a page label, returns a set of its ancestor category labels
        # !!!! Current priority !!!!
        # Only returns direct parents right now, not further ancestors
        pages = self.get_page_dict()
        catlinks = self.get_catlinks_dict()
        print ("Given node", node, ",", pages[node])
        p_ids = pages[node]
        visited_pages = p_ids.copy()
        print ("Corresponding ID should be", p_ids)
        
        categories = set()
        while (len(p_ids) != 0 and self.get_root() not in categories):
            
            page_id, page_namespace = p_ids.pop()
            print ("Grabbing categories pointing to id", page_id)
            if page_id in catlinks:
                for cat_name, page_type in catlinks[page_id]:
                    
                    cat_id = pages[cat_name][0]
                    
                    if cat_id[0] not in visited_pages:
                        print ("Found cat", cat_name, "of type", page_type)
                        
                        print ("Cat's id is", cat_id)
                        
                        categories.add(cat_name)
                        visited_pages.append(cat_id[0])
                        p_ids.append(cat_id)
        
        return categories
    
    def get_descendant_instances(self, node):
        # Given a category label, returns a set of its descendant page labels
        
        pages = self.get_page_dict()
        catlinks = self.get_catlinks_dict()
        
        if node not in catlinks:
            return set()
        
        descendants = set()
        visited_categories = [node]
        
        categories = [node]
        while (len(categories) != 0):
            category_name = categories.pop()
            print ( "Current cat:", category_name)
            
            for page_id, page_type in catlinks[category_name]:
                if page_id in pages:
                    for page_name, page_namespace in pages[page_id]:
                        
                        if page_type == "'page'":
                            descendants.add(page_name)
                        elif page_type == "'subcat'":
                            if page_name not in visited_categories and page_name in self.catlinks:
                                categories.append(page_name)
                                visited_categories.append(page_name)
        
        return descendants
        
    def get_page_dict(self):
        return copy.deepcopy(self.pages)
    
    def get_catlinks_dict(self):
        return copy.deepcopy(self.catlinks)

def getAllPages(pages_filename):
    print ("Pages")
    pages_file = open(pages_filename, 'r')
    
    pages = dict()
    for page in pages_file:
        page_id, page_namespace, page_title, page_is_redirect, page_len, page_content_model, page_lang = page.split('\t')
        # Ignores page_namespace = 1-13 and 15 because they are all metadata
        if int(page_namespace) == 0 or int(page_namespace) == 14 or int(page_namespace) > 15:
            if page_id in pages:
                pages[page_id].append( (page_title, page_namespace) )
            else:
                pages[page_id] = [ (page_title, page_namespace ) ]
            if page_title in pages:
                pages[page_title].append( (page_id, page_namespace) )
            else:
                pages[page_title] = [ (page_id, page_namespace) ]
#        print ("Pages[", page_id, "]:", pages[page_id])
    pages_file.close()
    return pages

def getAllCategories(catlinks_filename):
    print ("Categories")
    catlinks_file = open(catlinks_filename, 'r')
    
    cats = dict()
    for category in catlinks_file:
        page_id, cat_label, page_type = category.strip('\n').split('\t')
        if cat_label in cats:
            cats[cat_label].append( (page_id, page_type) )
        else:
            cats[cat_label] = [ (page_id, page_type) ]
        if page_id in cats:
            cats[page_id].append( (cat_label, page_type) )
        else:
            cats[page_id] = [ (cat_label, page_type) ]
#        print("cats[", cat_label, "]:", cats[cat_label])
    catlinks_file.close()
    return cats

def getCategoriesOfPage(root, catlinks_filename, p_id):
    catlinks_file = open(catlinks_filename, 'r')
    
    categories = set()
    for category in catlinks_file:
        page_id, cat_label, page_type = category.strip('\n').split('\t')
        if page_id == p_id:
            categories.add(cat_label)
    
    catlinks_file.close()
    return categories
