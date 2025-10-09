namespace sap.capire.bookshop;

entity Books {
  key ID : Integer;
  title  : String(100);
  author : Association to Authors;
  stock  : Integer;
  price  : Decimal(9,2);
}

entity Authors {
  key ID : Integer;
  name   : String(100);
  books  : Association to many Books on books.author = $self;
}