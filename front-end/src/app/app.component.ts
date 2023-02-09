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
  result_count: number | null;
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
  bookYear?: number;
  yearRadioButton = '=';
  ratingRadioButton = '=';


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

  rateData: any;
  yearData: any;
  rateStackData: any;
  infoData: any;

  lineChartOptions = {
    plugins: {
      legend: {
        labels: {
          color: '#495057'
        }
      }
    }
  };

  vertBarChartOptions = {
    plugins: {
      legend: {
        labels: {
          color: '#495057'
        }
      }
    }
  };

  stackedChartOptions = {
    tooltips: {
      mode: 'index',
      intersect: false
    },
    responsive: true,
    scales: {
      xAxes: [{
        stacked: true,
      }],
      yAxes: [{
        stacked: true,
      }]
    }
  };

  doughChartOptions = {
    plugins: {
      legend: {
        labels: {
          color: '#ebedef'
        }
      }
    },
    responsive: true
  };

  constructor(private http: HttpClient) {

    this.sortedBooks = this.books?.slice();
    this.getYearChartInstance();
    this.getRateChartInstance();
    this.getRateStackChartInstance();
    this.getInfoChartInstance();
  }


  handlePageEvent(e: PageEvent) {
    this.pageEvent = e;
    this.pageLength = e.length;
    this.pageSize = e.pageSize;
    this.pageIndex = e.pageIndex;
    this.search(false)
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
    await this.getAllGenres();
    
  }

  async loadData() {
    let url = this.url + 'load_data';
    this.loading = true;
    this.http.get<any>(url).subscribe(res => {
      if (res.success == true) {
        console.log('Success');
      }
      this.loading = false;
    });
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
      this.books[index].review = res.review;
      this.books[index].review_url = res.review_url;
      
      this.loading = false;
      if (this.books) {
        this.sortedBooks = this.books?.slice();
      }
      
    })
  }
  
  async search(reset = true) {
    this.pageIndex = reset ? 0 : this.pageIndex
    this.loading = true;
    console.log(this.bookTitle)
    let url = this.url + 'books?';
    if (this.bookTitle) {
      const bookTitle = this.bookTitle.replace('#','%23')
      url += 'title=' + bookTitle + '&';
    }
    if (this.bookAuthor) {
      url += 'author=' + this.bookAuthor + '&';
    } 
    if (this.bookGenre) {
      url += 'genre_name=' + this.bookGenre + '&';
    }
    if (this.bookRating) {
      url += 'average_rating=' + this.bookRating + '&' + 'rating-sign=' + this.ratingRadioButton + '&';
    }
    if (this.bookYear) {
      const filterDate = this.bookYear + '-01-01 00:00:00'
      url += 'date=' + filterDate + '&' + 'year-sign=' + this.yearRadioButton + '&';
    } 
    url += 'first=' + this.pageSize + '&' + 'skip=' + this.pageSize * this.pageIndex;
    this.http.get<BookResponse[]>(url).subscribe(res => {
      this.books = res;
      this.loading = false;
      if (this.books) {
        this.sortedBooks = this.books?.slice();
        this.showPagination = this.books.length > 0;
        this.pageLength = this.books[0].result_count || this.books.length
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


  getYearChartInstance() {
    this.loadYearData();
  }

  
  getRateChartInstance() {
    this.loadRateData();
  }
  
  getRateStackChartInstance() {
    this.loadRateStackData();
  }

  getInfoChartInstance() {
    this.loadInfoData();
  }

  async loadRateData() {
    let url = this.url + 'chart_rates';
    let newLabels:any[] = [];
    let newPoints:any[] = [];
    this.http.get<any[]>(url).subscribe( res => {
      if (res) {
        res.forEach( (val:any[]) => {
          newLabels.push(val[0]);
          newPoints.push(val[1]);
        });
      }
    });
    this.rateData = {
      labels: newLabels,
      datasets: [
        {
          label: 'amount of books',
          data: newPoints,
          backgroundColor: '#42A5F5',
          tension: .5,
        },
      ]
    };
  }


  async loadRateStackData() {
    let url = this.url + 'chart_rates_detail';
    let newdata:any[] = [];
    let newPoints: Array<Array<any>> = [[], [], [], [], [], [], []];
    let coloring = ['#42A5F5', '#33cc33', '#cccc00', '#ff6666', '#cc33ff', '#33cccc', '#cc44cc'];
    let getIndex = (value:any):number => {
      let ind = parseInt(value);
      if (ind < 6 && ind > -1) {
        return ind;
      } 
      return 6;
    }
    this.http.get<any[]>(url).subscribe( res => {
      if (res) {
        res.forEach( (val:any[]) => {
          let temp = newPoints[getIndex(val[0])];
          temp.push(val[2]);
        });
        newPoints.forEach( (val:any[], i:number) =>{
          let set = {
            type: 'bar',
            label: (i == 6) ? "no rating" : i.valueOf(),
            backgroundColor: coloring.pop(),
            data: val
          };
          newdata.push(set);
        });
      }
    });
    this.rateStackData = {
      labels: ['.0', '.1', '.2', '.3', '.4', '.5', '.6', '.7', '.8', '.9'],
      datasets: newdata
    };
  }

  async loadYearData() {
    let url = this.url + 'chart_years';
    let newLabels:any = [];
    let newPoints:any[] = [];
    this.http.get<any[]>(url).subscribe( res => {
      if (res) {
        res.forEach( (val:any[]) => {
          newLabels.push(val[0]);
          newPoints.push(val[1]);
        });
      }
    });
    this.yearData = {
      labels: newLabels,
      datasets: [
        {
          label: 'amount of books',
          data: newPoints,
          fill: false,
          borderColor: '#42A5F5',
          tension: .5,
        },
      ]
    };
  }

  async loadInfoData() {
    let url = this.url + 'chart_info';
    let newData:number[] = [];
    this.http.get<any[]>(url).subscribe( res => {
      if (res) {
        res.forEach((val:any[]) => {
          newData.push(val[0]);
          newData.push(val[1]);
        });
      }
    });
    this.infoData = {
      labels: ['Titles', 'Authors'],
      datasets: [
        {
          data: newData,
          backgroundColor: [
            '#42A5F5', 
            '#00F542'
          ],
          hoverBackgroundColor: [
            '#42A5F5', 
            '#00F542'
          ]
        },
      ]
    };
  }

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
