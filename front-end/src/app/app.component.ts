import { HttpClient } from '@angular/common/http';
import { Component } from '@angular/core';


interface BookResponse {
  book_id: number;
  title: string
  author: string;
  publication_date: string;
  review: string;
  review_url: string;
  page_count: number;
  price: number;
  rating: number;
}

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent {
  bookTitle?: string;
  bookAuthor?: string;
  url = 'http://localhost:5000/';
  books?: BookResponse[];
  displayedColumns: string[] = ['title', 'author', 'rating', 'review', 'review_url'];

  constructor(private http: HttpClient) {}
  
  async search() {
    let url = this.url;
    if (this.bookTitle) {
      url += 'books?title=' + this.bookTitle;
    } else if (this.bookAuthor) {
      url += 'books?author=' + this.bookAuthor;
    } else {
      url += 'all_books'
    }
    this.http.get<BookResponse[]>(url).subscribe(res => {
      console.log(res);
      this.books = res;
    })
  }
}
