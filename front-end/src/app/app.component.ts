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
    this.books?.push({author: 'Roald Dahl', genre: 'Thriller', book_id: 23, page_count: 120, price: 20, publication_date: '2002.01.13', rating: 8.0, review: `THE WITCHES, By Roald Dahl. Illustrated by Quentin Blake. 202 pp. New York: Farrar, Straus & Giroux. $10.95. (Ages 9 and Up)

    ROALD DAHL knows every bit as well as Bruno Bettelheim that children love the macabre, the terrifying, the mythic. In his latest book, ''The Witches,'' a 7-year-old orphan boy, cared for by his Norwegian grandmother, discovers the true nature of witches and then has the misfortune to be transformed into a mouse by the Grand High Witch of All the World - a horrifying creature with a bride-of-Frankenstein face concealed behind the mask of a pretty young woman. In this book, witches are characterized as figures of horror - baldheaded, claw-fingered, toeless women, their deformities hidden beneath pretty masks, fancy wigs, white gloves and pointy shoes.
    
    Although I have written a book arguing for the reha Erica Jong is the author of ''Witches.'' Her most recent book of poetry is ''Ordinary Miracles.'' bilitation of the witch as a descendant of the great mother goddess of the ancient world, I can certainly see what Roald Dahl is up to here. His witches must be horrifying creatures to underline his hero's heroism. For ''The Witches'' is a heroic tale. A schoolboy is transformed into a tiny mouse (with, however, the mind and language of a very bright child), and through his extraordinary bravery, he manages to save all the children of England from the same fate.
    
    Under the surface of this deceptively simple tale, which whizzes along and is great fun to read, lurks an interesting metaphor. This is the equation of childhood with mousedom. A child may be smaller than all the witchy, horrifying adults, but he can certainly outwit them. He is tiny and crushable, but he is also fast and well-nigh invisible. With the assistance of his benevolent Grandmamma (who hoists him up to things he can't reach, secretes him in her handbag, feeds and cuddles him), he is able to outsmart nearly the whole adult world.
    
    ''The Witches'' is also, in its way, a parable about the fear of death as separation and a child's mourning for the loss of his parents. Mr. Dahl's hero is happy when he is turned into a mouse - not only because of his speed and dexterity (and because he doesn't have to go to school) but also because his short life span now means that he will never have to be parted from his beloved grandmother as he has been from his parents. Already well into her 80's, she has only a few years to live, and he as a mouse-person is granted the same few years. Rather than bemoaning this, both grandmother and grandson rejoice that they can now count on living and dying together.
    
    The boy doesn't mind being a mouse, he says, because ''It doesn't matter who you are or what you look like so long as somebody loves you.'' And, indeed, the hero of this tale is loved. Whether as a boy or a mouse, he experiences the most extraordinary and unqualified approval from his grandmother - the sort of unconditional love adults and children alike crave.
    
    ''The Witches'' is finally a love story - the story of a little boy who loves his grandmother so utterly (and she him) that they are looking forward to spending their last years few exterminating the witches of the world together. It is a curious sort of tale but an honest one, which deals with matters of crucial importance to children: smallness, the existence of evil in the world, mourning, separation, death. The witches I've written about are far more benevolent figures, yet perhaps that is the point of witches - they are projections of the human unconscious and so can have many incarnations.`, review_url: 'https://www.nytimes.com/1983/11/13/books/the-boy-who-became-a-mouse.html', title: 'The Witches'});
    this.books?.push({author: 'Dale Carnegie',genre: 'Self-Help', book_id: 24, page_count: 320, price: 51, publication_date: '2013.06.11', rating: 8.6, review: null, review_url: null, title: 'How To Win Friends and Influence People'})
    this.books?.push({author: 'Laura Levine',genre: 'Thriller', book_id: 25, page_count: 204, price: 29.90, publication_date: '2015.09.23', rating: 8.0, review: null, review_url: null, title: 'Death of a Bachelorette'})
    this.books?.push({author: 'Agatha Christie',genre: 'Detective and Mystery', book_id: 26, page_count: 207, price: 19.80, publication_date: '1985.06.15', rating: 9.2, review: null, review_url: 'https://www.nytimes.com/2017/11/17/books/review/murder-orient-express-agatha-christie-audiobook-kenneth-branagh.html', title: 'Murder on the Orient Express'})
    this.books?.push({author: 'Ernest Cline',genre: 'Action', book_id: 27, page_count: 34, price: 25, publication_date: '2011.08.15', rating: 9.2, review: 'Ernest Clines “Ready Player One” is a book filled with references to video games, virtual reality, 80s pop-culture trivia, geek heroes like ', review_url: 'http://www.nytimes.com/2011/08/15/books/ready-player-one-by-ernest-cline-review.html', title: 'Ready Player One'})

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
