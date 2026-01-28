import { ChangeDetectorRef, Component, NgZone } from '@angular/core';

@Component({
  selector: 'app-upload-invoice.component',
  imports: [],
  templateUrl: './upload-invoice.component.html',
  styleUrl: './upload-invoice.component.css',
})
export class UploadInvoiceComponent {

  public invoiceFile: File | undefined;
  public invoicePreview: string | undefined //Para previsualizar necesitaremos la ruta de la imagen

  constructor(private zone: NgZone,
    private cdr: ChangeDetectorRef
  ) {}

  onFileChange(event: Event) {
    console.log("fichero subido");

    let target = event.target as HTMLInputElement;
    if (target.files !== null && target.files.length > 0) {
      this.invoiceFile = target.files[0]; // extraer el primer archivo

      // Opcional: Mostrar la imagen por pantalla para previsualizarla antes de subirla
      let reader = new FileReader();
      reader.onload = () => {
        this.zone.run(() => {
          this.invoicePreview = reader.result as string;
          console.log("Archivo previsualizado: ", this.invoicePreview);
           this.cdr.markForCheck();
        });
      };

      reader.readAsDataURL(this.invoiceFile);
      console.log(event);
      console.log("Archivo previsualizado: ", this.invoicePreview);
    }
  }

  save() {
    console.log("Archivo subido: ", this.invoicePreview);
    console.log("objeto", this.invoiceFile);
    

  }
}
