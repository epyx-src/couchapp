function(head, req) {
  // !code vendor/mustache.js
  // !code vendor/couchapp/couchapp.js
  // !code vendor/couchapp/rendering.js
  // !code vendor/couchapp/path.js
  // !json templates.<%plural_name%>.index
  // !json templates.layout

  provides("html", function() {
    var row, rows = [];
    while(row = getRow()) { rows.push(row['value']); };
    send(CouchApp.rendering.with_layout(templates, Mustache.to_html(templates.<%plural_name%>.index, {
      <%plural_name%>: rows,
      show_url: function() {
        return CouchApp.path.showPath('blog_post', this._id);
      }
    })));
  });
}
