import { animate, state, style, transition, trigger } from '@angular/animations';
import { HttpClient } from '@angular/common/http';
import { Component } from '@angular/core';
import { Sort } from '@angular/material/sort';


interface BookResponse {
  book_id: number| null;
  title: string | null;
  author: string | null;
  publication_date: string | null;
  review: string | null;
  review_url: string | null;
  page_count: number | null;
  price: number| null ;
  rating: number | null;
  genre: string | null;
}

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss'],
  animations: [
    trigger('detailExpand', [
      state('collapsed', style({height: '0px', minHeight: '0'})),
      state('expanded', style({height: '*'})),
      transition('expanded <=> collapsed', animate('225ms cubic-bezier(0.4, 0.0, 0.2, 1)')),
    ])]
})
export class AppComponent {
  bookTitle?: string;
  bookAuthor?: string;
  bookRating?: number;
  bookGenre?: string;
  options = [
    {value: 'Thriller', viewValue: 'Thriller'},
    {value: 'Comedy', viewValue: 'Comedy'},
    {value: 'Self-Help', viewValue: 'Self-Help'},
    {value: 'Action', viewValue: 'Action'}
  ];
  url = 'http://localhost:5000/';
  books: BookResponse[] = [];

  sortedBooks: BookResponse[];
  displayedColumns: string[] = ['title', 'author', 'rating','genre', 'review', 'review_url', 'page_count', 'price', 'publication_date'];
  displayedColumnsWithExpand = [...this.displayedColumns, 'expand']
  expandedReview?: BookResponse | null;

  constructor(private http: HttpClient) {
   

    this.sortedBooks = this.books?.slice();
  }
  
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
      if (this.books) {
        this.sortedBooks = this.books?.slice();
      }
      
    })
  }
  sortData(sort: Sort) {
    if (!this.books) {
      return
    }
    const data = this.books.slice();
    
    if (!sort.active || sort.direction === '') {
      this.sortedBooks = data;
      return;
    }

    this.sortedBooks = data.sort((a, b) => {
      const isAsc = sort.direction === 'asc';
      switch (sort.active) {
        case 'author':
          return compare(a.author || '', b.author || '', isAsc);
        case 'rating':
          return compare(a.rating || '', b.rating || '', isAsc);
        case 'page_count':
          return compare(a.page_count || '', b.page_count || '', isAsc);
        case 'price':
          return compare(a.price || '', b.price || '', isAsc);
        case 'title':
          return compare(a.title || '', b.title || '', isAsc);
        default:
          return 0;
      }
    });
  }
}

function compare(a: number | string, b: number | string, isAsc: boolean) {
  return (a < b ? -1 : 1) * (isAsc ? 1 : -1);
}
