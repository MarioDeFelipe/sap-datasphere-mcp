using { sap.capire.bookshop as my } from '../db/schema';

service CatalogService {
  @readonly entity Books as projection on my.Books;
  @readonly entity Authors as projection on my.Authors;
  
  action submitOrder (book: Books:ID, quantity: Integer) returns String;
  function getBooksByAuthor (author: String) returns array of Books;
}