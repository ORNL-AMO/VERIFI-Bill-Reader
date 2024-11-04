import { HttpClient } from '@angular/common/http';
import { Component } from '@angular/core';
//import { RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-root',
  standalone: true,
  //imports: [RouterOutlet],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent {
  title = 'pdf-upload';

  constructor(
    private http:HttpClient
  ){

  }
  name:string = ''
  file:any; 
  getName(name:string) {
    this.name = name;
  }

  getFile(event:any) {
    this.file = event.target.files[0];
    console.log('file',this.file);
  }

  submitData(){
    //formData object
    let formData = new FormData();
    formData.set("name",this.name)
    formData.set("file",this.file)

    //Submit to API
    this.http.post('http://127.0.0.1:8000/convert', formData).subscribe(
      (response)=>{}
    )
  }
}
