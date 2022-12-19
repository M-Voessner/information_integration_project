import { Component } from '@angular/core';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent {
  bookTitle?: string;
  bookAuthor?: string;

  search() {
    console.log(this.bookTitle)
  }
}
