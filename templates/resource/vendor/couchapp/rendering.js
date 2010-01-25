CouchApp.rendering = {
  with_layout: function(templates, content) {
    return(Mustache.to_html(templates.layout.application, {content: content}));
  },

  render_template: function(doc, templates, template, view_options) {
    return {
      code: 200,
      body: this.with_layout(templates, Mustache.to_html(template, view_options || {}))
    };
  }
};
