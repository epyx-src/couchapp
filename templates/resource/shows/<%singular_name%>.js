function(doc, req) {
  // !code vendor/mustache.js
  // !code vendor/couchapp/couchapp.js
  // !code vendor/couchapp/rendering.js
  // !code vendor/couchapp/path.js
  // !code vendor/couchapp/date.js
  // !json templates.<%plural_name%>.show
  // !json templates.layout
  
  return CouchApp.rendering.render_template(doc, templates, templates.<%plural_name%>.show, {
    <%singular_name%>: [doc],
    id: doc['_id'],
    edit_url: CouchApp.path.showPath('edit_<%singular_name%>', doc['_id']),
    list_url: CouchApp.path.listPath('<%plural_name%>', '<%plural_name%>'),
    update_url: CouchApp.path.updatePath('<%singular_name%>', doc['_id']) 
  });
}
