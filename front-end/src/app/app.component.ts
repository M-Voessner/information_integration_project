import { animate, state, style, transition, trigger } from '@angular/animations';
import { HttpClient } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { FormControl } from '@angular/forms';
import { PageEvent } from '@angular/material/paginator';
import { Sort } from '@angular/material/sort';
import { map, Observable, startWith, take } from 'rxjs';


interface BookResponse {
  book_id: number| null;
  author: string | null;
  title: string | null;
  ratings_count: number | null;
  currency: string | null;
  description: string | null;
  publisher: string | null;
  ISBN13: string | null;
  language: string | null;
  cover: string | null;
  publication_date: string | null;
  review: string | null;
  review_url: string | null;
  page_count: number | null;
  price: number| null ;
  average_rating: number | null;
  genre: string | null;
}

interface DropDownOption {
  value: string;
  viewValue: string;
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
  genreOptions: DropDownOption[] = [];
  url = 'http://localhost:5000/';
  books: BookResponse[] = [];

  sortedBooks: BookResponse[];
  displayedColumns: string[] = ['title', 'author', 'average_rating','genre', 'description', 'price', 'publication_date'];
  displayedColumnsWithExpand = [...this.displayedColumns, 'expand']
  expandedReview?: BookResponse | null;


  pageLength = 100;
  pageSize = 10;
  pageIndex = 0;
  pageSizeOptions = [10,25,50,100]
  pageEvent?: PageEvent;

  showPagination = true;

  constructor(private http: HttpClient) {

    this.sortedBooks = this.books?.slice();
  }


  handlePageEvent(e: PageEvent) {
    this.pageEvent = e;
    this.pageLength = e.length;
    this.pageSize = e.pageSize;
    this.pageIndex = e.pageIndex;
    this.search()
  }

  async ngOnInit() {
    this.search()
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
    await this.getAllGenres()
  }

  async getReview(book_id: any) {
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
      url += 'genre_name=' + this.bookGenre + '&';
    }
    if (this.bookRating) {
      url += 'average_rating=' + this.bookRating + '&';
    } 
    url += 'first=' + this.pageSize + '&' + 'skip=' + this.pageSize * this.pageIndex;
    this.http.get<BookResponse[]>(url).subscribe(res => {
      console.log(res);
      this.books = res;
      this.loading = false;
      if (this.books) {
        this.sortedBooks = this.books?.slice();
        this.showPagination = this.sortedBooks.length == this.pageSize;
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
        case 'average_rating':
          return compare(a.average_rating || '', b.average_rating || '', isAsc);
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
      this.pageLength = this.titleOptions.length
    });
  }

  async getAllAuthors() {
    let url = this.url + 'all_authors';
    this.http.get<any>(url).subscribe(res => {
      this.authorOptions = res;
    });
  }

  async getAllGenres() {
    let url = this.url + 'all_genres';
    this.http.get<any>(url).subscribe(res => {
      this.genreOptions = res.map((genre: string) => {
        return <DropDownOption> {
          value: genre,
          viewValue: genre
        }
      }); 
    })
  };

  private _filterTitles(value: string): string[] {
    const filterValue = value.toLowerCase();

    return this.titleOptions.filter(option => option.toLowerCase().startsWith(filterValue)).slice(0,50);
  }

  private _filterAuthors(value: string): string[] {
    const filterValue = value.toLowerCase();

    return this.authorOptions.filter(option => option.toLowerCase().startsWith(filterValue)).slice(0,50);
  }
}

function compare(a: number | string, b: number | string, isAsc: boolean) {
  return (a < b ? -1 : 1) * (isAsc ? 1 : -1);
}
