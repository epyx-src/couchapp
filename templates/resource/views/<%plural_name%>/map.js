function(doc) {
  if(doc.type == '<%singular_name%>') {
    emit(doc.created_at, doc);
  };
}
