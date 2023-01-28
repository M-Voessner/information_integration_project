import { animate, state, style, transition, trigger } from '@angular/animations';
import { HttpClient } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { FormControl } from '@angular/forms';
import { Sort } from '@angular/material/sort';
import { map, Observable, startWith } from 'rxjs';


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
export class AppComponent implements OnInit {
  formControlTitle = new FormControl('')
  formControlAuthor = new FormControl('')
  titleOptions: string[] = []
  authorOptions: string[] = []
  loading = false;

  filteredTitleOptions?: Observable<string[]>;
  filteredAuthorOptions?: Observable<string[]>;

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
  async ngOnInit() {
    await this.getAllTitles()
    this.filteredTitleOptions = this.formControlTitle.valueChanges.pipe(
      startWith(''),
      map(value => this._filterTitles(value || '')),
    );
    await this.getAllAuthors()
    this.filteredAuthorOptions = this.formControlAuthor.valueChanges.pipe(
      startWith(''),
      map(value => this._filterAuthors(value || '')),
    );
    
    
  }

  async getReview(book_id: any) {
    console.log(book_id);
    const index = this.books.findIndex(book => book.book_id === book_id);
    if (index > 0) {
      if (this.books[index].review_url != null) {
        return;
      }
    }
    this.loading = true;
    let url = this.url + 'get_review?book_id=' + book_id;
    this.http.get<any>(url).subscribe(res => {
      console.log(res);
      this.books[index].review = res.review;
      this.books[index].review_url = res.review_url;
      
      this.loading = false;
      if (this.books) {
        this.sortedBooks = this.books?.slice();
      }
      
    })
  }
  
  async search() {
    this.loading = true;
    let url = this.url + 'books?';
    if (this.bookTitle) {
      url += 'title=' + this.bookTitle + '&';
    }
    if (this.bookAuthor) {
      url += 'author=' + this.bookAuthor + '&';
    } 
    if (this.bookGenre) {
      url += 'genre=' + this.bookGenre + '&';
    }
    if (this.bookRating) {
      url += 'rating=' + this.bookRating + '&';
    } 
    url = url.slice(0,-1)
    this.http.get<BookResponse[]>(url).subscribe(res => {
      console.log(res);
      this.books = res;
      this.loading = false;
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

  async getAllTitles() {
    let url = this.url + 'all_titles';
    this.http.get<any>(url).subscribe(res => {
      this.titleOptions = res; 
      console.log(this.titleOptions);
    });
  }

  async getAllAuthors() {
    let url = this.url + 'all_authors';
    this.http.get<any>(url).subscribe(res => {
      this.authorOptions = res; 
      console.log(this.authorOptions)
    });
  }

  private _filterTitles(value: string): string[] {
    const filterValue = value.toLowerCase();

    return this.titleOptions.filter(option => option.toLowerCase().includes(filterValue));
  }

  private _filterAuthors(value: string): string[] {
    const filterValue = value.toLowerCase();

    return this.authorOptions.filter(option => option.toLowerCase().includes(filterValue));
  }
}

function compare(a: number | string, b: number | string, isAsc: boolean) {
  return (a < b ? -1 : 1) * (isAsc ? 1 : -1);
}
