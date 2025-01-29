import { HttpClient } from '@angular/common/http';
import { Component } from '@angular/core';
import { CommonModule } from '@angular/common'; // ✅ Import CommonModule
//import { RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule],
  //imports: [RouterOutlet],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent {
  title = 'pdf-upload';
 
  errorMessage: string = '';  //variable to hold error messages

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
    this.errorMessage = ''; //Clears any previous errors
    const allowedTypes = ['application/pdf', 'application/x-pdf'];
    // Validate the file type before sending the request
    if (!this.file || !allowedTypes.includes(this.file.type))  {
      this.errorMessage = 'Error uploading file. Please upload a valid PDF file.';
      return;
    }

    //formData object
    let formData = new FormData();
    //formData.set("name",this.name)
    formData.append("file",this.file) //send only the file
    //formData.set("file",this.file)

    //Submit to API
    this.http.post<any>('http://127.0.0.1:8000/convert', formData).subscribe({
    next: (response: any) => {
      console.log('File uploaded successfully', response);
      alert('File uploaded and processed successfully!');
    },
    error: (error: any) => {
      console.error('Error uploading file', error);
      this.errorMessage = error.error?.detail || 'An unexpected error occurred. Please try again.';
    }
  });
  }
}
