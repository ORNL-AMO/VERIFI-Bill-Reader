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
    if(!this.file) {
      this.errorMessage = 'No file selected. Please choose a PDF file.';
      return;
    }
    const fileExtension = this.file.name.split('.').pop()?.toLowerCase();
    if (!allowedTypes.includes(this.file.type) && fileExtension !== 'pdf')  {
      this.errorMessage = 'Error uploading file. Please upload a valid PDF file.';
      return;
    }

    //formData object
    let formData = new FormData();
    //formData.set("name",this.name)
    formData.append("file",this.file) //send only the file
    //formData.set("file",this.file)

    //Submit to API
    this.http.post('http://127.0.0.1:8000/convert', formData, { responseType: 'blob'}).subscribe({
    next: (response: any) => {
      if (!response || response.size === 0) {
        this.errorMessage = "Server returned an empty file. Please try again.";
        return;
      }
      
      // This portion allows the file to be automatically
      // downloaded, I am just leaving it commented out
      // so our computers don't get filled with random excel
      // files during testing

      // const fileURL = window.URL.createObjectURL(response);
      // const a = document.createElement('a');
      // a.href = fileURL;
      // a.download = `${this.file.name.replace('.pdf', '')}_data.xlsx`;
      // a.click();
      // window.URL.revokeObjectURL(fileURL);
    },
    error: (error: any) => {
      this.errorMessage = error.error?.detail || 'An unexpected error occurred. Please try again.';
    }
  });
  }
}
